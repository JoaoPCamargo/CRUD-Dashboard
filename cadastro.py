import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# CORRIGIDO: usar caminho raw string ou barras duplas/alternativas
DB_PATH = r"C:\sqlite\hqs.db"  # ajuste para o seu banco

class ComicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cadastro de Quadrinhos")
        self.conn = sqlite3.connect(DB_PATH)

        # --- EDITORA ---
        tk.Label(root, text="Editora:").grid(row=0, column=0, sticky="w")
        self.publisher_cb = ttk.Combobox(root, state="readonly")
        self.publisher_cb.grid(row=0, column=1, padx=5, pady=5)
        self.publisher_cb.bind("<<ComboboxSelected>>", self.load_series)

        # --- SÉRIE ---
        tk.Label(root, text="Série:").grid(row=1, column=0, sticky="w")
        self.series_cb = ttk.Combobox(root, state="readonly")
        self.series_cb.grid(row=1, column=1, padx=5, pady=5)
        self.series_cb.bind("<<ComboboxSelected>>", self.load_arcs)

        # --- ARCO ---
        tk.Label(root, text="Arco:").grid(row=2, column=0, sticky="w")
        self.arc_cb = ttk.Combobox(root, state="readonly")
        self.arc_cb.grid(row=2, column=1, padx=5, pady=5)

        # --- NÚMERO DA EDIÇÃO ---
        tk.Label(root, text="Número da Edição:").grid(row=3, column=0, sticky="w")
        self.issue_entry = tk.Entry(root)
        self.issue_entry.grid(row=3, column=1, padx=5, pady=5)

        # --- TÍTULO ---
        tk.Label(root, text="Título:").grid(row=4, column=0, sticky="w")
        self.title_entry = tk.Entry(root)
        self.title_entry.grid(row=4, column=1, padx=5, pady=5)

        # --- DATA DE LANÇAMENTO ---
        tk.Label(root, text="Data de Lançamento (YYYY-MM-DD):").grid(row=5, column=0, sticky="w")
        self.date_entry = tk.Entry(root)
        self.date_entry.grid(row=5, column=1, padx=5, pady=5)

        # --- BOTÃO SALVAR ---
        self.save_btn = tk.Button(root, text="Cadastrar Quadrinho", command=self.save_comic)
        self.save_btn.grid(row=6, column=0, columnspan=2, pady=10)

        self.load_publishers()

    def load_publishers(self):
        cur = self.conn.cursor()
        cur.execute("SELECT publisher_id, name FROM Publisher ORDER BY name")
        self.publishers = cur.fetchall()
        self.publisher_cb["values"] = [p[1] for p in self.publishers]

    def load_series(self, event=None):
        idx = self.publisher_cb.current()
        if idx < 0: 
            self.series_cb["values"] = []
            return

        publisher_id = self.publishers[idx][0]
        print(f"[DEBUG] Buscando séries para publisher_id={publisher_id}")

        cur = self.conn.cursor()
        cur.execute("SELECT series_id, name FROM Series WHERE publisher_id=? ORDER BY name", (publisher_id,))
        self.series = cur.fetchall()
        print(f"[DEBUG] Séries encontradas: {self.series}")

        if not self.series:
            messagebox.showinfo("Aviso", "Nenhuma série encontrada para esta editora.")
            self.series_cb["values"] = []
        else:
            self.series_cb["values"] = [s[1] for s in self.series]
        self.series_cb.set("")
        self.arc_cb.set("")
        self.arc_cb["values"] = []

    def load_arcs(self, event=None):
        idx = self.series_cb.current()
        if idx < 0:
            self.arc_cb["values"] = []
            return

        series_id = self.series[idx][0]
        cur = self.conn.cursor()
        cur.execute("SELECT arc_id, name FROM Arc WHERE series_id=? ORDER BY name", (series_id,))
        self.arcs = cur.fetchall()

        self.arc_cb["values"] = [a[1] for a in self.arcs]
        self.arc_cb.set("")

    def save_comic(self):
        try:
            issue = int(self.issue_entry.get())
        except ValueError:
            messagebox.showerror("Erro", "Número da edição inválido!")
            return

        title = self.title_entry.get().strip()
        date_str = self.date_entry.get().strip()
        release_date = None
        if date_str:
            try:
                release_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                messagebox.showerror("Erro", "Data inválida! Use YYYY-MM-DD")
                return

        series_idx = self.series_cb.current()
        if series_idx < 0:
            messagebox.showerror("Erro", "Selecione uma série!")
            return
        series_id = self.series[series_idx][0]

        arc_idx = self.arc_cb.current()
        arc_id = self.arcs[arc_idx][0] if arc_idx >= 0 else None

        cur = self.conn.cursor()
        cur.execute("INSERT INTO Comic (issue_number, title, release_date, series_id, arc_id) VALUES (?, ?, ?, ?, ?)",
                    (issue, title if title else None, release_date, series_id, arc_id))
        self.conn.commit()

        messagebox.showinfo("Sucesso", "Quadrinho cadastrado!")
        self.issue_entry.delete(0, tk.END)
        self.title_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.series_cb.set("")
        self.arc_cb.set("")

if __name__ == "__main__":
    root = tk.Tk()
    app = ComicApp(root)
    root.mainloop()
