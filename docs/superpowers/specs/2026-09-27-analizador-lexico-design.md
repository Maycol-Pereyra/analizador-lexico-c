# Analizador Léxico con FLEX — Diseño

## Objetivo

Tarea 2 de Compiladores: analizador léxico construido con FLEX, con documentación
del lenguaje de prueba, código fuente + ejecutable en GitHub, y una app gráfica
(no de consola) para probarlo.

## Lenguaje reconocido (mini-C)

Un subconjunto tipo C, elegido por cubrir todas las categorías clásicas de
token con un autómata simple de explicar:

| Categoría | Ejemplos | Regla |
|---|---|---|
| Palabras clave | `if else while for int float char void return` | literal exacta |
| Identificador | `contador`, `_x1` | `[a-zA-Z_][a-zA-Z0-9_]*` (si no es palabra clave) |
| Número entero | `42` | `[0-9]+` |
| Número decimal | `3.14` | `[0-9]+\.[0-9]+` |
| Cadena | `"hola\n"` | `"..."` con escapes `\"` `\\` `\n` |
| Operador | `+ - * / % = == != < > <= >= && \|\| !` | literales, maximal munch |
| Símbolo | `{ } ( ) ; ,` | literales |
| Comentario | `// linea`, `/* bloque */` | se descartan, no generan token |
| Espacios/saltos de línea | | se descartan, cuentan línea/columna |
| Error léxico | cualquier otro carácter (`@`, `$`, `#`, string sin cerrar) | token `ERROR` con línea/columna, el análisis continúa |

## Arquitectura

```
código fuente (.txt) 
      │
      ▼
lexer.exe   (generado: lexer.l --[win_flex]--> lex.yy.c --[cl.exe]--> lexer.exe)
      │  stdout: una línea por token → "TIPO|LEXEMA|LINEA|COLUMNA"
      ▼
gui/app.py (Tkinter)  --  ejecuta lexer.exe como subproceso, parsea stdout,
                          muestra tabla de tokens y resalta errores
```

- **`src/lexer.l`**: especificación Flex — el autómata real (estados, patrones,
  acciones). Es el corazón del entregable y lo que se explica en la
  presentación.
- **`src/lexer_main.c`**: `main()` mínimo que abre el archivo pasado por
  argumento, llama a `yylex()` en un loop hasta EOF y deja que las reglas de
  `lexer.l` impriman cada token.
- **`gui/app.py`**: única pieza de GUI. Editor de texto (cargar/pegar código),
  botón "Analizar", tabla de resultados (tipo, lexema, línea, columna), fila en
  rojo para `ERROR`. Se ejecuta como app de escritorio (`pythonw`/ventana
  Tkinter), nunca abre consola.
- **`tools/win_flex.exe`**: Flex portable para Windows (de winflexbison,
  descargado sin instalador). Se versiona en el repo para que compilar no
  requiera instalar nada.
- **`build.ps1`**: ubica Visual Studio con `vswhere`, importa el entorno de
  `cl.exe`, corre `win_flex` sobre `lexer.l` y compila a `lexer.exe`.
- **`tests/ejemplos/`**: 2-3 archivos mini-C de prueba (uno válido, uno con
  errores léxicos intencionales) para demo y para el README.

## Flujo de datos

1. Usuario escribe/carga código en la GUI y pulsa "Analizar".
2. La GUI escribe el texto a un archivo temporal y ejecuta
   `lexer.exe <archivo>` capturando stdout (sin mostrar consola:
   `subprocess.CREATE_NO_WINDOW`).
3. Cada línea de stdout (`TIPO|LEXEMA|LINEA|COLUMNA`) se parsea y se agrega a
   la tabla (`ttk.Treeview`).
4. Si `lexer.exe` no existe todavía, la GUI muestra un aviso pidiendo correr
   `build.ps1` primero (no se auto-compila desde la GUI: mantiene la GUI
   simple y el build explícito).

## Manejo de errores

- Carácter no reconocido → token `ERROR` con posición, el lexer sigue
  analizando el resto del archivo (no aborta).
- Cadena sin cerrar al llegar a fin de línea → token `ERROR` para esa cadena.
- Archivo vacío → tabla vacía, sin crash.

## Testing

- `tests/ejemplos/valido.txt` — programa mini-C sin errores, cubre todas las
  categorías de token.
- `tests/ejemplos/con_errores.txt` — incluye caracteres inválidos y una cadena
  sin cerrar, para demostrar que el `ERROR` se reporta y el análisis continúa.
- Verificación manual: correr `lexer.exe` sobre ambos desde línea de comandos
  y confirmar la salida antes de dar por buena la GUI; luego repetir desde la
  GUI y comparar visualmente.

## Fuera de alcance

- Análisis sintáctico/semántico (es solo léxico).
- Recuperación de errores sofisticada (basta con reportar y continuar).
- Empaquetado como `.exe` de la GUI (se entrega el `.py`; Python + Tkinter
  vienen preinstalados, no hace falta instalador).

## Entregables finales (GitHub)

- Código fuente (`src/`, `gui/`, `build.ps1`, `tools/win_flex.exe`).
- Ejecutable compilado `lexer.exe` (se compila y se commitea tras el build).
- `README.md` con la tabla de tokens de arriba, diagrama de arquitectura,
  explicación del autómata (para la exposición) e instrucciones de
  build/ejecución.
