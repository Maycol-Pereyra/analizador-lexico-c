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
