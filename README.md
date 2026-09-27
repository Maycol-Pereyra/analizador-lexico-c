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
