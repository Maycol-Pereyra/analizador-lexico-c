$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

$vswhere = "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"
$vsPath = & $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (-not $vsPath) {
    $vsPath = & $vswhere -latest -products * -property installationPath
}
$vcvars = Join-Path $vsPath "VC\Auxiliary\Build\vcvars64.bat"

$flex = Join-Path $root "tools\win_flex.exe"
$lexerL = Join-Path $root "src\lexer.l"
$lexYyC = Join-Path $root "src\lex.yy.c"
$lexerMain = Join-Path $root "src\lexer_main.c"
$outExe = Join-Path $root "lexer.exe"

Write-Host "Generando lexer con win_flex..."
& $flex --outfile=$lexYyC $lexerL
if ($LASTEXITCODE -ne 0) { throw "win_flex fallo" }

Write-Host "Compilando con cl.exe..."
$cmd = "call `"$vcvars`" >nul && cl.exe /nologo /Fe:`"$outExe`" `"$lexYyC`" `"$lexerMain`""
cmd.exe /c $cmd
if ($LASTEXITCODE -ne 0) { throw "cl.exe fallo" }

Remove-Item -ErrorAction SilentlyContinue (Join-Path $root "lexer.obj"), (Join-Path $root "lex.yy.obj"), (Join-Path $root "lexer_main.obj")

Write-Host "OK: $outExe"
