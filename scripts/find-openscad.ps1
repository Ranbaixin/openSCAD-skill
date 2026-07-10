# find-openscad.ps1
# Discover OpenSCAD path on Windows
# Returns the first found path, or exits with error if not found.

# 1. Check PATH first
$pathResult = Get-Command openscad -ErrorAction SilentlyContinue
if ($pathResult) {
    Write-Output $pathResult.Source
    exit 0
}

# 2. Check default 64-bit install location
$default64 = "C:\Program Files\OpenSCAD\openscad.exe"
if (Test-Path $default64) {
    Write-Output $default64
    exit 0
}

# 3. Check 32-bit install location
$default32 = "C:\Program Files (x86)\OpenSCAD\openscad.exe"
if (Test-Path $default32) {
    Write-Output $default32
    exit 0
}

# 4. Check nightly build location
$nightly = "C:\Program Files\OpenSCAD (Nightly)\openscad.exe"
if (Test-Path $nightly) {
    Write-Output $nightly
    exit 0
}

# 5. Check user-local scoop/choco installs
$scoop = "$env:USERPROFILE\scoop\apps\openscad\current\openscad.exe"
if (Test-Path $scoop) {
    Write-Output $scoop
    exit 0
}

# 6. Not found
Write-Error "openscad.exe: not found in PATH or standard locations"
Write-Error "Install from: https://openscad.org/downloads.html"
exit 1
