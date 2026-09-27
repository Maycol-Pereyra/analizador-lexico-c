$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$exe = Join-Path $root "lexer.exe"

function Assert-Contains($lines, $needle) {
    if (-not ($lines -match [regex]::Escape($needle))) {
        throw "Esperaba encontrar linea que contenga: $needle"
    }
}

Write-Host "Probando valido.txt..."
$out1 = & $exe (Join-Path $root "tests\ejemplos\valido.txt")
Assert-Contains $out1 "PALABRA_CLAVE|int|1|1"
Assert-Contains $out1 "IDENTIFICADOR|contador|1"
Assert-Contains $out1 "DECIMAL|3.14"
Assert-Contains $out1 "OPERADOR|=="
Assert-Contains $out1 "CADENA|`"hola mundo`""
if ($out1 -match "ERROR") { throw "valido.txt no deberia producir ERROR" }
Write-Host "OK valido.txt ($($out1.Count) tokens)"

Write-Host "Probando con_errores.txt..."
$out2 = & $exe (Join-Path $root "tests\ejemplos\con_errores.txt")
Assert-Contains $out2 "ERROR|@"
$errorCount = ($out2 | Select-String "^ERROR").Count
if ($errorCount -lt 2) { throw "esperaba al menos 2 tokens ERROR, hubo $errorCount" }
Write-Host "OK con_errores.txt ($errorCount errores detectados, analisis continuo)"

Write-Host "TODOS LOS TESTS PASARON"
