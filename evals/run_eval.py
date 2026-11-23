"""Run 12 independent, matched local-model tool sessions. No cloud endpoint or shell tool."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from urllib.request import Request, urlopen

import trimesh

ROOT = Path(__file__).resolve().parents[1]
TASKS = json.loads(Path(__file__).with_name("tasks.json").read_text(encoding="utf-8"))
FIXTURE = ROOT / "examples/intermediate/assembly-fit/enclosure.scad"
TOOLS = """You are the user's CAD file agent. Work in the trial directory. Each turn select one real tool using JSON fields.
list: list working files and available renderer.
read: file (a SCAD or Markdown working file).
reference: file (a repository reference path relative to the skill root).
edit: source, file, old, new. Replace exactly one occurrence in source and save to file.
write: file, text. Write a SCAD or Markdown file.
render: file (SCAD), output (new STL). Render default parameters.
verify: file (SCAD). Run the enclosure baseline and 3 mm variant verifier. It creates both print files and a JSON report.
inspect: file (STL). Save measured facts to inspection.json.
repair: file (STL), output (new STL), filter (all or largest). Run STL repair.
finish: state (verified, inspected, unrendered, or unverified), text (your final answer to the user).
File tools allow changes to the trial inputs. There is no general shell. Use actual tool results. Respond with a single action."""
FIELDS = {"list": (), "read": ("file",), "reference": ("file",),
          "edit": ("source","file","old","new"), "write": ("file","text"),
          "render": ("file","output"), "verify": ("file",), "inspect": ("file",),
          "repair": ("file","output","filter"), "finish": ("state","text")}
SCHEMA = {"oneOf": []}
for name, fields in FIELDS.items():
    props = {"tool": {"type":"string","enum":[name]}, **{key:{"type":"string"} for key in fields}}
    if name == "finish":
        props["state"]["enum"] = ["verified","inspected","unrendered","unverified"]
    if name == "repair":
        props["filter"]["enum"] = ["all","largest"]
    SCHEMA["oneOf"].append({"type":"object","properties":props,"required":["tool",*fields],
                            "additionalProperties":False})


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def package_hashes():
    files = [ROOT/"SKILL.md", FIXTURE, *sorted((ROOT/"evals").glob("*.py")),
             ROOT/"evals/tasks.json", *sorted((ROOT/"scripts").glob("*.py")),
             *sorted((ROOT/"references").glob("*.md")), *sorted((ROOT/"examples").rglob("*.md"))]
    return {p.relative_to(ROOT).as_posix():digest(p) for p in files}


def prepare(task, work):
    work.mkdir()
    if task == "wall":
        shutil.copyfile(FIXTURE, work/"source.scad")
    if task == "offline":
        (work/"existing.scad").write_bytes(b"cube([6,6,1]);\n")
    if task == "pair":
        a = trimesh.creation.box(extents=[20,10,3])
        b = trimesh.creation.box(extents=[4,4,4])
        b.apply_translation([22,0,0])
        trimesh.util.concatenate([a,b]).export(work/"pair.stl")
    return {f.name: digest(f) for f in work.iterdir()}


def local_file(work, name):
    if not name or not isinstance(name, str) or Path(name).name != name or ":" in name or "\\" in name:
        raise ValueError("use a single filename in the trial directory")
    path = (work/name).resolve()
    if path.parent != work.resolve():
        raise ValueError("file outside trial directory")
    return path


def invoke_tool(task, work, action):
    kind = action["tool"]
    if kind == "list":
        return {"files": sorted(p.name for p in work.iterdir()), "openscad_available": task != "offline"}
    if kind == "reference":
        path = (ROOT/action["file"]).resolve()
        if (path.suffix != ".md" or not any(path.is_relative_to(ROOT/p) for p in ("references","examples"))):
            raise ValueError("choose a reference under examples/ or references/")
        return {"text": path.read_text(encoding="utf-8")[:5000]}
    path = local_file(work, action["file"])
    if kind in ("read","edit","write"):
        if path.suffix not in (".scad",".md"):
            raise ValueError("text tools operate on .scad and .md")
        if kind == "read":
            return {"text": path.read_text(encoding="utf-8")[:8000]}
        if kind == "edit":
            source = local_file(work, action["source"])
            text = source.read_text(encoding="utf-8")
            if not action["old"] or text.count(action["old"]) != 1:
                raise ValueError("old text must occur exactly once")
            text = text.replace(action["old"], action["new"], 1)
        else:
            text = action["text"]
        path.write_text(text, encoding="utf-8")
        return {"written": path.name, "sha256": digest(path)}
    if task == "offline" and kind in ("verify", "render"):
        return {"error": "OpenSCAD is unavailable to this agent", "executed": False}
    if kind == "render":
        from scripts.validate_scad import OpenSCAD, find_openscad
        out = local_file(work, action["output"])
        if out.suffix != ".stl":
            raise ValueError("choose an STL output")
        rec = OpenSCAD.probe(find_openscad()).render(path, out)
        return {"exit_code": rec["exit_code"], "error": rec.get("error"), "output": out.name}
    if kind == "verify":
        args = ["verify_assembly.py", "--model", str(path), "--out", str(work/"evidence")]
    elif kind == "inspect":
        args = ["inspect_stl.py", str(path), "--json"]
    elif kind == "repair":
        args = ["repair_stl.py", str(path), str(local_file(work, action["output"])), "--json"]
        if action.get("filter") == "largest":
            args.append("--keep-largest")
    else:
        raise ValueError("unknown tool")
    proc = subprocess.run([sys.executable, "-X", "utf8", str(ROOT/"scripts"/args[0]), *args[1:]],
                          capture_output=True, encoding="utf-8", timeout=300)
    result = {"exit_code": proc.returncode}
    if proc.returncode:
        result["error"] = (proc.stderr or proc.stdout)[-1600:]
    elif kind == "verify":
        report_path = Path(proc.stdout.strip().split(" ", 1)[1])
        report = json.loads(report_path.read_text(encoding="utf-8"))
        result.update(report=report_path.relative_to(work).as_posix(), status=report["status"],
                      checks=len(report["checks"]), model_sha256=report["model_sha256"])
    elif kind == "inspect":
        data = json.loads(proc.stdout)
        save(work/"inspection.json", data)
        result.update(report="inspection.json", components=data["component_count"],
                      extents_mm=data["extents_mm"], watertight=data["watertight"])
    else:
        result["status"] = json.loads(proc.stdout)["status"]
    return result


def loaded_model(identifier):
    process = subprocess.run(["lms","ps","--json"], capture_output=True, text=True, check=True)
    for model in json.loads(process.stdout):
        if model["identifier"] == identifier:
            return {k: model.get(k) for k in ("identifier","modelKey","selectedVariant","quantization","contextLength","parallel")}
    raise RuntimeError(f"model instance not loaded: {identifier}")


def episode(root, task, arm, seed, config):
    folder = root/f"{task}-{arm}-{seed}"
    folder.mkdir()
    work = folder/"work"
    initial = prepare(task, work)
    system = TOOLS
    if arm == "on":
        system += "\n\nInstalled skill:\n" + (ROOT/"SKILL.md").read_text(encoding="utf-8")
    messages = [{"role":"system", "content":system}, {"role":"user", "content":TASKS[task]}]
    trace = {"task":task, "arm":arm, "seed":seed, "source_hashes":initial, "turns":[],
             "status":"INDETERMINATE", "model_instance":loaded_model(config["model"])}
    save(folder/"trace.json", trace)
    try:
        for _ in range(config["max_steps"]):
            body = {"model":config["model"], "messages":messages, "seed":seed,
                    "temperature":config["temperature"], "max_tokens":config["max_tokens"],
                    "response_format":{"type":"json_schema","json_schema":{"name":"action","schema":SCHEMA,"strict":True}}}
            req = Request(config["endpoint"], json.dumps(body).encode("utf-8"), {"Content-Type":"application/json"})
            with urlopen(req, timeout=180) as response:
                answer = json.load(response)
            if answer.get("model") != config["model"]:
                raise RuntimeError(f"unexpected served model: {answer.get('model')}")
            msg = answer["choices"][0]["message"]["content"]
            turn = {"response_id":answer.get("id"), "model":answer.get("model"), "response":msg,
                    "usage":answer.get("usage"), "finish_reason":answer["choices"][0].get("finish_reason")}
            trace["turns"].append(turn)
            messages.append({"role":"assistant","content":msg})
            try:
                action = json.loads(msg)
                turn["action"] = action
                if action["tool"] == "finish":
                    trace.update(status="FINISHED", final=action)
                    break
                result = invoke_tool(task, work, action)
            except (KeyError, ValueError, OSError, subprocess.SubprocessError) as exc:
                result = {"error":str(exc)}
            turn["result"] = result
            messages.append({"role":"user", "content":json.dumps(result, ensure_ascii=False)})
            save(folder/"trace.json", trace)
        else:
            trace["status"] = "STEP_LIMIT"
        if loaded_model(config["model"]) != trace["model_instance"]:
            raise RuntimeError("model instance changed during trial")
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as exc:
        trace.update(status="INDETERMINATE", error=str(exc))
    finally:
        save(folder/"trace.json", trace)
    print(folder.name, trace["status"], flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="loaded LM Studio instance identifier")
    parser.add_argument("--weights", type=Path, required=True, help="corresponding local GGUF, hashed before and after")
    parser.add_argument("--port", type=int, default=1234)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="ab-",dir=args.out.resolve()))
    config = {"endpoint":f"http://127.0.0.1:{args.port}/v1/chat/completions","model":args.model,
              "instance":loaded_model(args.model), "weights":args.weights.name, "sha256":digest(args.weights),
              "skill_sha256":digest(ROOT/"SKILL.md"), "fixture_sha256":digest(FIXTURE), "tasks":TASKS,
              "package_sha256":package_hashes(),
              "system_without_skill":TOOLS, "tool_schema":SCHEMA, "max_steps":9, "max_tokens":700,
              "temperature":0.2, "paired_seeds":[1711,1712],
              "runtime":subprocess.check_output(["lms","--version"],text=True).strip()}
    save(root/"manifest.json",config)
    print(root, flush=True)
    for i, seed in enumerate(config["paired_seeds"]):
        for task in TASKS:
            for arm in (("off","on") if i == 0 else ("on","off")):
                episode(root, task, arm, seed, config)
    config["identity_verified"] = (digest(args.weights) == config["sha256"] and
                                   loaded_model(args.model) == config["instance"] and
                                   package_hashes() == config["package_sha256"])
    save(root/"manifest.json",config)
    if not config["identity_verified"]:
        raise RuntimeError("model or tool package changed over the paired run")
    from score import score_suite
    score_suite(root)


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    main()
