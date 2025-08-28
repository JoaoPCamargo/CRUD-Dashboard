import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from tkcalendar import DateEntry
from config import DASHBOARD_PATH
from db.queries import (
    get_publishers, insert_publisher,
    get_series_by_publisher, insert_series,
    get_arcs_by_series, insert_arc,
    insert_comic
)

class ComicAdd:
    def __init__(self, root):
        self.root = root
        self.root.title("Cadastro de Quadrinhos")

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
        self.date_entry = DateEntry(root, width=12, background='purple', foreground='red', borderwidth=2)
        self.date_entry.grid(row=5, column=1, padx=5, pady=5)
        self.date_entry.delete(0, tk.END)

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

        # --- BOTÕES ---
        self.save_btn = tk.Button(root, text="Cadastrar Quadrinho", command=self.save_comic)
        self.save_btn.grid(row=7, column=0, padx=5, pady=10)

        self.dash_btn = tk.Button(root, text="📊", width=3, command=self.open_dashboard)
        self.dash_btn.grid(row=7, column=1, padx=5, pady=10, sticky="w")

        self.back_btn = tk.Button(root, text="Voltar ao Menu", command=self.back_to_menu)
        self.back_btn.grid(row=7, column=2, padx=5, pady=10)

        # Carrega dados iniciais
        self.load_publishers()

    # --- LOADERS ---
    def load_publishers(self):
        self.publishers = get_publishers()
        self.publisher_cb["values"] = [p[1] for p in self.publishers]

    def load_series(self, event=None):
        idx = self.publisher_cb.current()
        if idx < 0:
            self.series_cb["values"] = []
            self.arc_cb.set("")
            self.arc_cb["values"] = []
            return

        publisher_id = self.publishers[idx][0]
        self.series = get_series_by_publisher(publisher_id)
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
        self.arcs = get_arcs_by_series(series_id)
        self.arc_cb["values"] = [a[1] for a in self.arcs]
        self.arc_cb.set("")

    # --- ADD FUNCTIONS ---
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
            try:
                insert_publisher(nome)
                self.load_publishers()
                messagebox.showinfo("Sucesso", "Editora adicionada!", parent=win)
                win.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao adicionar editora: {e}", parent=win)

        tk.Button(win, text="Salvar", command=salvar).pack(pady=10)

    def add_series(self):
        idx = self.publisher_cb.current()
        if idx < 0:
            messagebox.showerror("Erro", "Selecione uma editora antes de criar a série!")
            return
        publisher_id = self.publishers[idx][0]

        win = tk.Toplevel(self.root)
        win.title("Nova Série")

        tk.Label(win, text="Nome da Série:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        entry_name = tk.Entry(win)
        entry_name.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(win, text="Ano de Início:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        entry_start_year = tk.Entry(win)
        entry_start_year.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(win, text="Ano de Fim:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        entry_end_year = tk.Entry(win)
        entry_end_year.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(win, text="Total de Edições:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        entry_total_issues = tk.Entry(win)
        entry_total_issues.grid(row=3, column=1, padx=10, pady=5)

        def salvar():
            nome = entry_name.get().strip()
            start_year = int(entry_start_year.get()) if entry_start_year.get().isdigit() else None
            end_year = int(entry_end_year.get()) if entry_end_year.get().isdigit() else None
            total_issues = int(entry_total_issues.get()) if entry_total_issues.get().isdigit() else None

            if not nome:
                messagebox.showerror("Erro", "Nome da série não pode ser vazio!", parent=win)
                return

            try:
                insert_series(nome, publisher_id, start_year, end_year, total_issues)
                self.load_series()
                messagebox.showinfo("Sucesso", "Série adicionada!", parent=win)
                win.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao adicionar série: {e}", parent=win)

        tk.Button(win, text="Salvar", command=salvar).grid(row=4, column=0, columnspan=2, pady=10)

    def add_arc(self):
        idx = self.series_cb.current()
        if idx < 0:
            messagebox.showerror("Erro", "Selecione uma série antes de criar o arco!")
            return
        series_id = self.series[idx][0]

        win = tk.Toplevel(self.root)
        win.title("Novo Arco")

        tk.Label(win, text="Nome do Arco:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        entry_name = tk.Entry(win)
        entry_name.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(win, text="Última Edição (end_issue):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        entry_end = tk.Entry(win)
        entry_end.grid(row=1, column=1, padx=10, pady=5)

        def salvar():
            nome = entry_name.get().strip()
            end_issue_str = entry_end.get().strip()
            end_issue = int(end_issue_str) if end_issue_str.isdigit() else None

            if not nome:
                messagebox.showerror("Erro", "Nome do arco não pode ser vazio!", parent=win)
                return

            try:
                insert_arc(nome, series_id, start_issue=1, end_issue=end_issue)
                self.load_arcs()
                messagebox.showinfo("Sucesso", "Arco adicionado!", parent=win)
                win.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao adicionar arco: {e}", parent=win)

        tk.Button(win, text="Salvar", command=salvar).grid(row=2, column=0, columnspan=2, pady=10)

    # --- SALVAR QUADRINHO ---
    def save_comic(self):
        try:
            issue = int(self.issue_entry.get())
        except ValueError:
            messagebox.showerror("Erro", "Número da edição inválido!")
            return

        title = self.title_entry.get().strip()
        date_str = self.date_entry.get().strip()
        reading_date = None
        if date_str:
            try:
                reading_date = datetime.strptime(date_str, "%m/%d/%y").date()
                if reading_date > date.today():
                    messagebox.showerror("Erro", "A data de leitura não pode ser no futuro!")
                    return
            except ValueError:
                messagebox.showerror("Erro", "Data inválida!")
                return

        series_idx = self.series_cb.current()
        if series_idx < 0:
            messagebox.showerror("Erro", "Selecione uma série!")
            return
        series_id = self.series[series_idx][0]

        arc_idx = self.arc_cb.current()
        arc_id = self.arcs[arc_idx][0] if arc_idx >= 0 else None

        avaliacao = self.avaliacao_var.get() or None

        try:
            insert_comic(issue, title if title else None, reading_date, series_id, arc_id, avaliacao)
            messagebox.showinfo("Sucesso", "Quadrinho cadastrado!")
            self.issue_entry.delete(0, tk.END)
            self.title_entry.delete(0, tk.END)
            self.date_entry.delete(0, tk.END)
            self.series_cb.set("")
            self.arc_cb.set("")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar quadrinho: {e}")

    # --- OUTROS ---
    def open_dashboard(self):
        popup = tk.Toplevel(self.root)
        popup.title("Dashboard")
        tk.Label(popup, text="Abrindo o dashboard...").pack(padx=20, pady=20)
        popup.update()
        os.startfile(DASHBOARD_PATH)
        popup.after(1000, popup.destroy)

    def set_stars(self, n):
        self.avaliacao_var.set(n)
        for i, lbl in enumerate(self.stars, start=1):
            lbl.config(text="★" if i <= n else "☆", fg="gold" if i <= n else "gray")

    def set_back_func(self, func):
        self.back_func = func

    def back_to_menu(self):
        if hasattr(self, 'back_func'):
            self.back_func()
