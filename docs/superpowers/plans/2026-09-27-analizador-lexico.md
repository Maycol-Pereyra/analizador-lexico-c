# Analizador Léxico (FLEX + GUI Tkinter) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a FLEX-based lexical analyzer for a mini-C language, wrapped in a Tkinter GUI, documented, and pushed to GitHub with source + compiled executable.

**Architecture:** `src/lexer.l` (Flex spec) → `win_flex` → `lex.yy.c` → compiled with MSVC `cl.exe` (via `src/lexer_main.c` driver) → `lexer.exe`. `gui/app.py` (Tkinter) runs `lexer.exe` as a hidden subprocess and renders tokens in a table.

**Tech Stack:** Flex (win_flex.exe, bundled portable binary), C (MSVC, Visual Studio Community already installed), Python 3.13 + Tkinter (stdlib, no install needed).

## Global Constraints

- No console window may ever appear to the user — GUI only (per assignment requirement 5).
- Lexical errors must be reported as an `ERROR` token with line/column and must NOT stop analysis of the rest of the file (per spec's "Manejo de errores").
- `tools/win_flex.exe` is already downloaded and present at repo root `tools/win_flex.exe` — do not re-download.
- Token output format from `lexer.exe` is fixed: one line per token, `TIPO|LEXEMA|LINEA|COLUMNA`, e.g. `IDENTIFICADOR|contador|3|5`. Every later task depends on this exact format.
- Repo root: `C:\Users\mayco\Desktop\Universidad\2026\3-2026\Compiladores\Tarea 2 - AnalizadorLexico` (already `git init`-ed, first commit is the spec doc).

---

### Task 1: Flex lexer + C driver + build script

**Files:**
- Create: `src/lexer.l`
- Create: `src/lexer_main.c`
- Create: `build.ps1`
- Create: `tests/ejemplos/valido.txt`
- Create: `tests/ejemplos/con_errores.txt`
- Test: `tests/test_lexer.ps1`

**Interfaces:**
- Produces: `lexer.exe` (built at repo root by `build.ps1`), a CLI program invoked as `lexer.exe <archivo>` that prints one line per token to stdout in the format `TIPO|LEXEMA|LINEA|COLUMNA` and exits 0. Token types used: `PALABRA_CLAVE`, `IDENTIFICADOR`, `ENTERO`, `DECIMAL`, `CADENA`, `OPERADOR`, `SIMBOLO`, `ERROR`.
- Consumes: `tools/win_flex.exe` (already present), MSVC `cl.exe` (located via `vswhere.exe` at `C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe`).

- [ ] **Step 1: Write `src/lexer.l`**

```c
%{
#include <stdio.h>
#include <string.h>

static int col = 1;

static void emit(const char *type) {
    printf("%s|%s|%d|%d\n", type, yytext, yylineno, col);
    col += (int)strlen(yytext);
}
%}

%option noyywrap
%option yylineno

%%

"if"|"else"|"while"|"for"|"int"|"float"|"char"|"void"|"return"   { emit("PALABRA_CLAVE"); }

[a-zA-Z_][a-zA-Z0-9_]*        { emit("IDENTIFICADOR"); }

[0-9]+\.[0-9]+                { emit("DECIMAL"); }
[0-9]+                        { emit("ENTERO"); }

\"([^\"\\\n]|\\.)*\"          { emit("CADENA"); }

"=="|"!="|"<="|">="|"&&"|"\|\|"|"+"|"-"|"*"|"/"|"%"|"="|"<"|">"|"!"   { emit("OPERADOR"); }

"{"|"}"|"("|")"|";"|","       { emit("SIMBOLO"); }

"//"[^\n]*                    { /* comentario de linea: se descarta */ }
"/*"([^*]|\*+[^*/])*\*+"/"    { /* comentario de bloque: se descarta */ }

\"([^\"\\\n]|\\.)*             { emit("ERROR"); }

\n                             { col = 1; }
[ \t\r]+                       { col += (int)yyleng; }

.                               { emit("ERROR"); }

%%
```

- [ ] **Step 2: Write `src/lexer_main.c`**

```c
#include <stdio.h>

extern int yylex(void);
extern FILE *yyin;

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "uso: lexer.exe <archivo>\n");
        return 1;
    }
    yyin = fopen(argv[1], "r");
    if (!yyin) {
        fprintf(stderr, "no se pudo abrir: %s\n", argv[1]);
        return 1;
    }
    yylex();
    fclose(yyin);
    return 0;
}
```

- [ ] **Step 3: Write `build.ps1`**

```powershell
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
```

- [ ] **Step 4: Write test fixtures**

`tests/ejemplos/valido.txt`:
```c
int contador;
float pi = 3.14;
if (contador == 10) {
    contador = contador + 1;
} else {
    contador = 0;
}
// comentario de linea
/* comentario
   de bloque */
char *msg = "hola mundo";
```

`tests/ejemplos/con_errores.txt`:
```c
int x = 5;
int y = @x;
char *s = "cadena sin cerrar
int z $ = 3;
```

- [ ] **Step 5: Build it**

Run: `powershell -ExecutionPolicy Bypass -File build.ps1`
Expected: prints `Generando lexer con win_flex...`, `Compilando con cl.exe...`, `OK: <path>\lexer.exe`, and `lexer.exe` exists at repo root.

- [ ] **Step 6: Write `tests/test_lexer.ps1`**

```powershell
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
```

- [ ] **Step 7: Run the test and verify it passes**

Run: `powershell -ExecutionPolicy Bypass -File tests\test_lexer.ps1`
Expected: ends with `TODOS LOS TESTS PASARON`, no exceptions thrown.

- [ ] **Step 8: Commit**

```bash
git add src/lexer.l src/lexer_main.c build.ps1 tests/ejemplos tests/test_lexer.ps1
git commit -m "Add Flex lexer, C driver, and build script for mini-C tokenizer"
```

---

### Task 2: Tkinter GUI

**Files:**
- Create: `gui/app.py`
- Test: `gui/test_parse.py`

**Interfaces:**
- Consumes: `lexer.exe` at repo root (built by Task 1), stdout format `TIPO|LEXEMA|LINEA|COLUMNA`.
- Produces: `parse_token_line(line: str) -> tuple[str, str, str, str]` in `gui/app.py`, used by `gui/test_parse.py`.

- [ ] **Step 1: Write `gui/test_parse.py` (failing test first)**

```python
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gui.app import parse_token_line


def test_parse_simple_token():
    assert parse_token_line("IDENTIFICADOR|contador|3|5") == ("IDENTIFICADOR", "contador", "3", "5")


def test_parse_token_with_pipe_in_lexeme():
    # una cadena podria contener el caracter '|': se debe unir todo lo sobrante en el lexema
    assert parse_token_line('CADENA|"a|b"|1|1') == ("CADENA", '"a|b"', "1", "1")


def test_parse_empty_line_returns_none():
    assert parse_token_line("") is None
    assert parse_token_line("   ") is None


if __name__ == "__main__":
    test_parse_simple_token()
    test_parse_token_with_pipe_in_lexeme()
    test_parse_empty_line_returns_none()
    print("TODOS LOS TESTS PASARON")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python gui\test_parse.py`
Expected: `ModuleNotFoundError` or `ImportError` (because `gui/app.py` does not exist yet).

- [ ] **Step 3: Write `gui/app.py`**

```python
import os
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import ttk, messagebox

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEXER_EXE = os.path.join(ROOT_DIR, "lexer.exe")


def parse_token_line(line):
    line = line.rstrip("\n").rstrip("\r")
    if not line.strip():
        return None
    parts = line.split("|")
    if len(parts) < 4:
        return None
    tipo = parts[0]
    linea = parts[-2]
    columna = parts[-1]
    lexema = "|".join(parts[1:-2])
    return (tipo, lexema, linea, columna)


def run_lexer(source_text):
    if not os.path.exists(LEXER_EXE):
        raise FileNotFoundError(
            "No se encontro lexer.exe. Corre build.ps1 primero para compilarlo."
        )
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        f.write(source_text)
        tmp_path = f.name
    try:
        creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        result = subprocess.run(
            [LEXER_EXE, tmp_path],
            capture_output=True,
            text=True,
            creationflags=creationflags,
        )
    finally:
        os.remove(tmp_path)
    tokens = []
    for line in result.stdout.splitlines():
        parsed = parse_token_line(line)
        if parsed:
            tokens.append(parsed)
    return tokens


class LexerApp:
    def __init__(self, root):
        self.root = root
        root.title("Analizador Lexico - Mini-C")
        root.geometry("900x600")

        paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        left = ttk.Frame(paned)
        paned.add(left, weight=1)

        ttk.Label(left, text="Codigo fuente:").pack(anchor="w")
        self.text = tk.Text(left, wrap="none", font=("Consolas", 11))
        self.text.pack(fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill=tk.X, pady=6)
        ttk.Button(btn_frame, text="Analizar", command=self.analizar).pack(side=tk.LEFT)
        self.status = ttk.Label(btn_frame, text="")
        self.status.pack(side=tk.LEFT, padx=10)

        right = ttk.Frame(paned)
        paned.add(right, weight=1)

        ttk.Label(right, text="Tokens:").pack(anchor="w")
        columns = ("tipo", "lexema", "linea", "columna")
        self.tree = ttk.Treeview(right, columns=columns, show="headings")
        for col, width in zip(columns, (140, 260, 60, 70)):
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=width)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.tag_configure("error", background="#ffcccc")

    def analizar(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        source = self.text.get("1.0", tk.END)
        try:
            tokens = run_lexer(source)
        except FileNotFoundError as e:
            messagebox.showerror("Falta compilar", str(e))
            return
        errores = 0
        for tipo, lexema, linea, columna in tokens:
            tag = "error" if tipo == "ERROR" else ""
            if tag:
                errores += 1
            self.tree.insert("", tk.END, values=(tipo, lexema, linea, columna), tags=(tag,) if tag else ())
        self.status.config(
            text=f"{len(tokens)} tokens, {errores} errores"
        )


def main():
    root = tk.Tk()
    LexerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python gui\test_parse.py`
Expected: `TODOS LOS TESTS PASARON`

- [ ] **Step 5: Manual smoke test of the GUI**

Run: `python gui\app.py` (with `lexer.exe` already built by Task 1)
Expected: window opens (no console flash), paste contents of `tests/ejemplos/con_errores.txt` into the left pane, click "Analizar", right pane shows a token table with `ERROR` rows highlighted in red and a status line like "N tokens, M errores".

- [ ] **Step 6: Commit**

```bash
git add gui/app.py gui/test_parse.py
git commit -m "Add Tkinter GUI wrapping lexer.exe"
```

---

### Task 3: README documentation

**Files:**
- Create: `README.md`
- Create: `.gitignore`

**Interfaces:**
- Consumes: token table and architecture from the spec (`docs/superpowers/specs/2026-09-27-analizador-lexico-design.md`), the exact `build.ps1` / `lexer.exe` / `gui/app.py` names from Tasks 1-2.

- [ ] **Step 1: Write `.gitignore`**

```
*.obj
src/lex.yy.c
__pycache__/
*.pyc
```

Note: `lexer.exe` and `tools/win_flex.exe` are intentionally NOT ignored — the assignment requires submitting the compiled executable.

- [ ] **Step 2: Write `README.md`**

```markdown
# Analizador Lexico - Mini-C (FLEX + Tkinter)

Analizador lexico construido con **FLEX**, con una GUI de escritorio en
Python/Tkinter para probarlo (sin consola).

## Lenguaje reconocido

| Categoria | Ejemplos | Patron |
|---|---|---|
| Palabra clave | `if else while for int float char void return` | literal exacta |
| Identificador | `contador`, `_x1` | `[a-zA-Z_][a-zA-Z0-9_]*` |
| Entero | `42` | `[0-9]+` |
| Decimal | `3.14` | `[0-9]+\.[0-9]+` |
| Cadena | `"hola\n"` | `"..."` con escapes |
| Operador | `+ - * / % = == != < > <= >= && \|\| !` | literales |
| Simbolo | `{ } ( ) ; ,` | literales |
| Comentario | `// linea`, `/* bloque */` | se descarta |
| Error lexico | `@`, `$`, cadena sin cerrar, etc. | token `ERROR` con linea/columna, el analisis continua |

## Arquitectura

```
codigo fuente (.txt)
      |
      v
lexer.exe  (src/lexer.l --[win_flex]--> src/lex.yy.c --[cl.exe]--> lexer.exe)
      |  stdout: "TIPO|LEXEMA|LINEA|COLUMNA" por linea
      v
gui/app.py (Tkinter) -- ejecuta lexer.exe oculto, muestra tabla de tokens
```

## El automata (para la exposicion)

`src/lexer.l` compila a un **automata finito determinista (AFD)** generado por
Flex. Cada regla (`if|else|...`, `[a-zA-Z_][a-zA-Z0-9_]*`, `[0-9]+`, etc.) se
traduce a una expresion regular, que Flex convierte primero a un AFN
(Thompson) y luego a un AFD minimizado con subset construction. Flex resuelve
ambiguedades con dos reglas: **maximal munch** (siempre consume la cadena
reconocible mas larga: `==` gana sobre `=` seguido de `=`) y **orden de
declaracion** (si dos patrones matchean lo mismo, gana el que aparece primero
en el archivo — por eso las palabras clave estan antes que el patron general
de identificador). El estado de error (`.`) es la regla de menor prioridad:
solo se activa si ninguna otra regla matcheo el caracter actual, y en vez de
frenar el automata, emite un token `ERROR` y sigue desde el siguiente caracter
(recuperacion por "descarte de caracter").

## Requisitos

- Windows con Visual Studio (Community/Build Tools) instalado — se usa
  `cl.exe` para compilar el C que genera Flex.
- Python 3.10+ (con Tkinter, incluido por defecto).
- `tools/win_flex.exe` ya viene incluido en el repo (Flex portable para
  Windows, de [winflexbison](https://github.com/lexxmark/winflexbison)), no
  hace falta instalar nada mas.

## Build

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1
```

Genera `lexer.exe` en la raiz del repo.

## Tests

```powershell
powershell -ExecutionPolicy Bypass -File tests\test_lexer.ps1
python gui\test_parse.py
```

## Ejecutar la app grafica

```powershell
python gui\app.py
```

Pega o escribe codigo mini-C en el panel izquierdo, click en "Analizar", y la
tabla de la derecha muestra cada token con su linea y columna (los `ERROR` se
resaltan en rojo).

## Estructura del repo

```
src/lexer.l          especificacion Flex (el automata)
src/lexer_main.c      driver en C que llama a yylex()
build.ps1             genera lex.yy.c con win_flex y compila con cl.exe
gui/app.py            GUI Tkinter
tests/ejemplos/       programas mini-C de prueba
tests/test_lexer.ps1  test de linea de comandos sobre lexer.exe
gui/test_parse.py     test del parser de tokens de la GUI
tools/win_flex.exe    Flex portable para Windows (bundled)
lexer.exe             ejecutable compilado (entregable)
```
```

- [ ] **Step 3: Commit**

```bash
git add README.md .gitignore
git commit -m "Add README with token table, architecture, and automaton explanation"
```

---

### Task 4: Push to GitHub

**Files:** none (repo operations only)

**Interfaces:** none

- [ ] **Step 1: Confirm the compiled `lexer.exe` is committed**

Run: `git status --short`
Expected: clean, or only shows files intentionally untracked per `.gitignore`. If `lexer.exe` shows as untracked, run `git add lexer.exe` and commit it (`git commit -m "Add compiled lexer.exe"`) — the assignment requires submitting the executable.

- [ ] **Step 2: Ask the user for the GitHub repo name/visibility, then create and push**

Ask the user (do not guess): desired repo name and whether it should be public or private. Then:

```bash
gh repo create <nombre-elegido> --source=. --<public|private> --push
```

Expected: command prints the new repo URL; `git remote -v` now shows `origin` pointing at it.

- [ ] **Step 3: Verify on GitHub**

Run: `gh repo view --web` (or share the printed URL with the user) and confirm `lexer.exe`, `src/`, `gui/`, `README.md` are all visible in the repo.

---

## Self-review notes

- Spec coverage: mini-C token table (Task 1 lexer.l + Task 3 README table), Flex requirement (Task 1), GUI-only requirement (Task 2, `CREATE_NO_WINDOW`), error tokens continue analysis (Task 1 `.` rule + Task 1 test), documentation of test language (Task 3 README), GitHub source+exe (Task 4), automaton explanation for the presentation (Task 3 README section) — all covered.
- Type/format consistency: `TIPO|LEXEMA|LINEA|COLUMNA` used identically in `lexer.l`'s `emit()`, `test_lexer.ps1`, and `gui/app.py`'s `parse_token_line`/`run_lexer`. Token type strings (`PALABRA_CLAVE`, `IDENTIFICADOR`, `ENTERO`, `DECIMAL`, `CADENA`, `OPERADOR`, `SIMBOLO`, `ERROR`) match between `lexer.l` and README.
- No placeholders remain; every step has literal file contents or exact commands.
