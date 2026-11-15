# CorridorKey 2.0 for Nuke - Windows installer bootstrap.
# Installs a private Miniforge (conda) into <backend>\_conda if it is missing, then runs install_backend.py
# with that Python - so the machine does not need its own Python, git or ffmpeg.
# Usage (via install_windows.bat): install_windows.bat [--backend D:\CorridorKey2.0] [--nuke-dir %USERPROFILE%\.nuke]

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"      # Invoke-WebRequest is very slow with the progress bar on
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$backend = Join-Path $env:USERPROFILE "CorridorKey2.0"
for ($i = 0; $i -lt $args.Count; $i++) {
    if ($args[$i] -eq "--backend" -and ($i + 1) -lt $args.Count) { $backend = $args[$i + 1] }
}
$backend = [IO.Path]::GetFullPath($backend)
# conda can't be installed into a path with spaces: then use the root of the same drive (matches install_backend.py)
if ($backend.Contains(" ")) { $condaRoot = Join-Path ([IO.Path]::GetPathRoot($backend)) "CorridorKey_conda" }
else { $condaRoot = Join-Path $backend "_conda" }
$condaPy = Join-Path $condaRoot "python.exe"

if (-not (Test-Path $condaPy)) {
    Write-Host "`n=== Miniforge (private conda for CorridorKey) -> $condaRoot"
    New-Item -ItemType Directory -Force -Path $backend | Out-Null
    $exe = Join-Path $env:TEMP "Miniforge3-Windows-x86_64.exe"
    $url = "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe"
    Write-Host "  downloading $url"
    Invoke-WebRequest -Uri $url -OutFile $exe -UseBasicParsing
    Write-Host "  installing (takes a minute)..."
    $p = Start-Process -FilePath $exe -Wait -PassThru -ArgumentList `
        "/InstallationType=JustMe /RegisterPython=0 /AddToPath=0 /NoRegistry=1 /NoShortcuts=1 /S /D=$condaRoot"
    Remove-Item $exe -ErrorAction SilentlyContinue
    if (-not (Test-Path $condaPy)) { throw "Miniforge did not install into $condaRoot (exit code $($p.ExitCode))." }
    Write-Host "  done"
}

& $condaPy -s (Join-Path $PSScriptRoot "install_backend.py") @args
exit $LASTEXITCODE
