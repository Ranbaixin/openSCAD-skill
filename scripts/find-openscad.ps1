# find-openscad.ps1
# Discover OpenSCAD path on Windows
# Returns the first found path, or exits with error if not found.

# 0. Respect an explicit override.
if ($env:OPENSCAD -and (Test-Path -LiteralPath $env:OPENSCAD)) {
    Write-Output $env:OPENSCAD
    exit 0
}

# 1. Check PATH first. Windows installs may expose openscad.com rather than .exe.
foreach ($commandName in @("openscad", "openscad.com", "openscad.exe")) {
    $pathResult = Get-Command $commandName -ErrorAction SilentlyContinue
    if ($pathResult) {
        Write-Output $pathResult.Source
        exit 0
    }
}

# 2. Check default 64-bit install location
$default64 = @("C:\Program Files\OpenSCAD\openscad.com", "C:\Program Files\OpenSCAD\openscad.exe")
foreach ($candidate in $default64) { if (Test-Path $candidate) { Write-Output $candidate; exit 0 } }

# 3. Check 32-bit install location
$default32 = @("C:\Program Files (x86)\OpenSCAD\openscad.com", "C:\Program Files (x86)\OpenSCAD\openscad.exe")
foreach ($candidate in $default32) { if (Test-Path $candidate) { Write-Output $candidate; exit 0 } }

# 4. Check nightly build location
$nightly = @("C:\Program Files\OpenSCAD (Nightly)\openscad.com", "C:\Program Files\OpenSCAD (Nightly)\openscad.exe")
foreach ($candidate in $nightly) { if (Test-Path $candidate) { Write-Output $candidate; exit 0 } }

# 5. Check user-local scoop/choco installs
$scoop = @("$env:USERPROFILE\scoop\apps\openscad\current\openscad.com", "$env:USERPROFILE\scoop\apps\openscad\current\openscad.exe")
foreach ($candidate in $scoop) { if (Test-Path $candidate) { Write-Output $candidate; exit 0 } }

# 6. Not found
Write-Error "openscad.exe: not found in PATH or standard locations"
Write-Error "Install from: https://openscad.org/downloads.html"
exit 1
