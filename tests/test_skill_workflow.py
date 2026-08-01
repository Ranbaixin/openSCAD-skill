from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = ROOT / "SKILL.md"


def _skill_text() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


def test_skill_uses_at_most_one_confirmation_round():
    text = _skill_text()
    required_rules = (
        "最多一轮集中确认",
        "能从输入文件或上下文确定的信息不要提问",
        "用户已提供或批准实施方案",
        "低风险遗漏",
        "尺寸、孔位、装配方向或主体轮廓",
        "回答后直接执行，不再进行第二次确认",
    )

    for rule in required_rules:
        assert rule in text

    assert "先用 ASCII 草图和一组最小问题确认" not in text


def test_skill_keeps_modeling_and_validation_contract_compact():
    text = _skill_text()

    assert "参数化建模" in text
    assert "几何验证" in text
    assert "不覆盖用户原始文件" in text
    assert "ASCII 草图仅用于" in text
    assert len(text.splitlines()) <= 120
