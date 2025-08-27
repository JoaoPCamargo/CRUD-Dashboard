import sqlite3
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry
from datetime import date

DB_PATH = r"C:\CRUD-Dashboard\hqs.db"  # ajuste para o seu banco

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

        self.add_pub_btn = tk.Button(root, text="+", command=self.add_publisher)
        self.add_pub_btn.grid(row=0, column=2, padx=5)

        # --- SÉRIE ---
        tk.Label(root, text="Série:").grid(row=1, column=0, sticky="w")
        self.series_cb = ttk.Combobox(root, state="readonly")
        self.series_cb.grid(row=1, column=1, padx=5, pady=5)
        self.series_cb.bind("<<ComboboxSelected>>", self.load_arcs)

        self.add_series_btn = tk.Button(root, text="+", command=self.add_series)
        self.add_series_btn.grid(row=1, column=2, padx=5)

        # --- ARCO ---
        tk.Label(root, text="Arco:").grid(row=2, column=0, sticky="w")
        self.arc_cb = ttk.Combobox(root, state="readonly")
        self.arc_cb.grid(row=2, column=1, padx=5, pady=5)

        self.add_arc_btn = tk.Button(root, text="+", command=self.add_arc)
        self.add_arc_btn.grid(row=2, column=2, padx=5)

        # --- NÚMERO DA EDIÇÃO ---
        tk.Label(root, text="Número da Edição:").grid(row=3, column=0, sticky="w")
        self.issue_entry = tk.Entry(root)
        self.issue_entry.grid(row=3, column=1, padx=5, pady=5)

        # --- TÍTULO ---
        tk.Label(root, text="Título:").grid(row=4, column=0, sticky="w")
        self.title_entry = tk.Entry(root)
        self.title_entry.grid(row=4, column=1, padx=5, pady=5)

        # --- DATA DE LEITURA ---
        tk.Label(root, text="Data de Leitura:").grid(row=5, column=0, sticky="w")
        self.date_entry = DateEntry(root, width=12, background='purple', foreground='red', borderwidth=2, year=2025)
        self.date_entry.grid(row=5, column=1, padx=5, pady=5)

        # --- AVALIAÇÃO ---
        tk.Label(root, text="Avaliação:").grid(row=6, column=0, sticky="w")
        self.avaliacao_var = tk.IntVar(value=0)

        stars_frame = tk.Frame(root)
        stars_frame.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        self.stars = []
        for i in range(1, 6):
            lbl = tk.Label(stars_frame, text="☆", font=("Arial", 18))
            lbl.grid(row=0, column=i, padx=2)
            lbl.bind("<Button-1>", lambda e, n=i: self.set_stars(n))
            self.stars.append(lbl)


        # --- BOTÃO SALVAR ---
        self.save_btn = tk.Button(root, text="Cadastrar Quadrinho", command=self.save_comic)
        self.save_btn.grid(row=7, column=0, padx=5, pady=10)

        # --- BOTÃO DASHBOARD ---
        self.dash_btn = tk.Button(root, text="📊", width=3, command=self.open_dashboard)
        self.dash_btn.grid(row=7, column=1, padx=5, pady=10, sticky="w")

        self.load_publishers()

    def load_publishers(self):
        cur = self.conn.cursor()
        cur.execute("SELECT publisher_id, name FROM Publisher ORDER BY name")
        self.publishers = cur.fetchall()
        self.publisher_cb["values"] = [p[1] for p in self.publishers]

    def add_publisher(self):
        win = tk.Toplevel(self.root)
        win.title("Nova Editora")

        tk.Label(win, text="Nome da Editora:").pack(padx=10, pady=5)
        entry = tk.Entry(win)
        entry.pack(padx=10, pady=5)

        def salvar():
            nome = entry.get().strip()
            if not nome:
                messagebox.showerror("Erro", "Nome da editora não pode ser vazio!", parent=win)
                return
            cur = self.conn.cursor()
            try:
                cur.execute("INSERT INTO Publisher (name) VALUES (?)", (nome,))
                self.conn.commit()
                self.load_publishers()  # atualiza a lista
                messagebox.showinfo("Sucesso", "Editora adicionada!", parent=win)
                win.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", "Essa editora já existe!", parent=win)

        tk.Button(win, text="Salvar", command=salvar).pack(pady=10)

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

    def add_series(self):
        idx = self.publisher_cb.current()
        if idx < 0:
            messagebox.showerror("Erro", "Selecione uma editora antes de criar a série!")
            return
        publisher_id = self.publishers[idx][0]

        win = tk.Toplevel(self.root)
        win.title("Nova Série")

        # Nome da série
        tk.Label(win, text="Nome da Série:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        entry_name = tk.Entry(win)
        entry_name.grid(row=0, column=1, padx=10, pady=5)

        # Ano de início
        tk.Label(win, text="Ano de Início:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        entry_start_year = tk.Entry(win)
        entry_start_year.grid(row=1, column=1, padx=10, pady=5)

        # Ano de fim
        tk.Label(win, text="Ano de Fim:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        entry_end_year = tk.Entry(win)
        entry_end_year.grid(row=2, column=1, padx=10, pady=5)

        # Total de edições
        tk.Label(win, text="Total de Edições:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        entry_total_issues = tk.Entry(win)
        entry_total_issues.grid(row=3, column=1, padx=10, pady=5)

        def salvar():
            nome = entry_name.get().strip()
            start_year_str = entry_start_year.get().strip()
            end_year_str = entry_end_year.get().strip()
            total_issues_str = entry_total_issues.get().strip()

            if not nome:
                messagebox.showerror("Erro", "Nome da série não pode ser vazio!", parent=win)
                return

            # Validações de inteiros ou NULL
            start_year = int(start_year_str) if start_year_str.isdigit() else None
            end_year = int(end_year_str) if end_year_str.isdigit() else None
            total_issues = int(total_issues_str) if total_issues_str.isdigit() else None

            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO Series (name, publisher_id, start_year, end_year, total_issues)
                VALUES (?, ?, ?, ?, ?)
            """, (nome, publisher_id, start_year, end_year, total_issues))
            self.conn.commit()

            self.load_series()
            messagebox.showinfo("Sucesso", "Série adicionada!", parent=win)
            win.destroy()

        tk.Button(win, text="Salvar", command=salvar).grid(row=4, column=0, columnspan=2, pady=10)

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

    def add_arc(self):
        idx = self.series_cb.current()
        if idx < 0:
            messagebox.showerror("Erro", "Selecione uma série antes de criar o arco!")
            return
        series_id = self.series[idx][0]

        win = tk.Toplevel(self.root)
        win.title("Novo Arco")

        # Nome do arco
        tk.Label(win, text="Nome do Arco:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        entry_name = tk.Entry(win)
        entry_name.grid(row=0, column=1, padx=10, pady=5)

        # End issue (usuário digita ou deixa em branco)
        tk.Label(win, text="Última Edição (end_issue):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        entry_end = tk.Entry(win)
        entry_end.grid(row=1, column=1, padx=10, pady=5)

        def salvar():
            nome = entry_name.get().strip()
            end_issue_str = entry_end.get().strip()

            if not nome:
                messagebox.showerror("Erro", "Nome do arco não pode ser vazio!", parent=win)
                return

            if end_issue_str == "":
                end_issue = None  # salva NULL
            elif end_issue_str.isdigit():
                end_issue = int(end_issue_str)
            else:
                messagebox.showerror("Erro", "Última edição deve ser número ou ficar em branco!", parent=win)
                return

            start_issue = 1  # fixo

            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO Arc (name, series_id, start_issue, end_issue)
                VALUES (?, ?, ?, ?)
            """, (nome, series_id, start_issue, end_issue))
            self.conn.commit()

            self.load_arcs()
            messagebox.showinfo("Sucesso", "Arco adicionado!", parent=win)
            win.destroy()

        tk.Button(win, text="Salvar", command=salvar).grid(row=2, column=0, columnspan=2, pady=10)

    def save_comic(self):

        try:
            issue = int(self.issue_entry.get())
        except ValueError:
            messagebox.showerror("Erro", "Número da edição inválido!")
            return

        title = self.title_entry.get().strip()
        #date_str = self.date_entry.get().strip()
        reading_date = self.date_entry.get_date()
        if reading_date > date.today():
            messagebox.showerror("Erro", "A data de leitura não pode ser no futuro!")
            return

        series_idx = self.series_cb.current()
        if series_idx < 0:
            messagebox.showerror("Erro", "Selecione uma série!")
            return
        series_id = self.series[series_idx][0]

        arc_idx = self.arc_cb.current()
        arc_id = self.arcs[arc_idx][0] if arc_idx >= 0 else None

        avaliacao = self.avaliacao_var.get()
        if avaliacao == 0:
            avaliacao = None

        cur = self.conn.cursor()
        cur.execute("INSERT INTO Comic (issue_number, title, reading_date, series_id, arc_id, rating) VALUES (?, ?, ?, ?, ?, ?)",
                    (issue, title if title else None, reading_date, series_id, arc_id, avaliacao))
        self.conn.commit()

        messagebox.showinfo("Sucesso", "Quadrinho cadastrado!")
        self.issue_entry.delete(0, tk.END)
        self.title_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.series_cb.set("")
        self.arc_cb.set("")

    def open_dashboard(self):
        # cria popup temporário
        popup = tk.Toplevel(self.root)
        popup.title("Dashboard")
        label = tk.Label(popup, text="Abrindo o dashboard...")
        label.pack(padx=20, pady=20)
        popup.update()

        # abre o arquivo do Power BI
        os.startfile(r"C:\CRUD-Dashboard\DashHQs.pbix")

        # fecha o popup após 1s
        popup.after(1000, popup.destroy)

    def set_stars(self, n):
        self.avaliacao_var.set(n)
        for i, lbl in enumerate(self.stars, start=1):
            if i <= n:
                lbl.config(text="★", fg="gold")
            else:
                lbl.config(text="☆", fg="gray")

if __name__ == "__main__":
    root = tk.Tk()
    app = ComicApp(root)
    root.mainloop()