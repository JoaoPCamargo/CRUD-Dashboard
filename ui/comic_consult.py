import os
import tkinter as tk
from tkinter import ttk
from ui.edit_comic import EditComicWindow
from db.queries import get_all_comics, get_filter_options, get_comics_by_filters
from config import DASHBOARD_PATH, ICON_PATH
from utils.validators import validate_int
from utils.helpers import rating_to_stars


class ComicConsult:
    def __init__(self, master, back_func):
        self.master = master
        self.master.title("Consultar Quadrinhos")
        self.master.iconbitmap(ICON_PATH)
        self.master.geometry("950x500")
        self.back_func = back_func

        # --- FRAME DOS BOTÕES SUPERIORES ---
        btn_frame = tk.Frame(master)
        btn_frame.pack(pady=5)

        self.back_btn = tk.Button(btn_frame, text="Voltar ao Menu", command=self.voltar)
        self.back_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.dash_btn = tk.Button(btn_frame, text="📊", width=3, command=self.open_dashboard)
        self.dash_btn.pack(side=tk.LEFT)

        # --- FRAME DOS FILTROS ---
        filtros_frame = ttk.LabelFrame(master, text="Filtros")
        filtros_frame.pack(fill="x", padx=10, pady=5)

        # Título
        tk.Label(filtros_frame, text="Título:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_titulo = tk.Entry(filtros_frame, width=25)
        self.entry_titulo.grid(row=0, column=1, padx=5, pady=5)

        # Edição
        tk.Label(filtros_frame, text="Edição:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        vcmd = master.register(validate_int)
        self.entry_edicao = tk.Entry(
            filtros_frame,
            width=10,
            validate="key",
            validatecommand=(vcmd, "%P")
        )
        self.entry_edicao.grid(row=0, column=3, padx=5, pady=5)

        # Série
        tk.Label(filtros_frame, text="Série:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.combo_serie = ttk.Combobox(filtros_frame, state="readonly", width=25)
        self.combo_serie.grid(row=1, column=1, padx=5, pady=5)

        # Arco
        tk.Label(filtros_frame, text="Arco:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.combo_arco = ttk.Combobox(filtros_frame, state="readonly", width=25)
        self.combo_arco.grid(row=1, column=3, padx=5, pady=5)

        # Editora
        tk.Label(filtros_frame, text="Editora:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.combo_editora = ttk.Combobox(filtros_frame, state="readonly", width=25)
        self.combo_editora.grid(row=2, column=1, padx=5, pady=5)

        # Botões de ação
        self.btn_pesquisar = ttk.Button(filtros_frame, text="Pesquisar", command=self.apply_filters)
        self.btn_pesquisar.grid(row=3, column=0, columnspan=2, pady=8)

        self.btn_limpar = ttk.Button(filtros_frame, text="Limpar Filtros", command=self.clear_filters)
        self.btn_limpar.grid(row=3, column=2, columnspan=2, pady=8)

        # --- TREEVIEW ---
        self.cols = ("ID", "Título", "Edição", "Data de Leitura", "Editora", "Série", "Arco", "Avaliação")
        self.tree = ttk.Treeview(master, columns=self.cols, show="headings")
        for col in self.cols:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c, False))
            self.tree.column(col, width=120)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.sort_orders = {col: False for col in self.cols}
        self.tree.bind("<Double-1>", self.on_double_click)

        # Carregar dados
        self.load_filter_options()
        self.load_comics()

    # ---------- FUNÇÕES INTERNAS ----------

    def load_filter_options(self):
        series, arcos, editoras = get_filter_options()
        self.combo_serie["values"] = series
        self.combo_serie.current(0)
        self.combo_arco["values"] = arcos
        self.combo_arco.current(0)
        self.combo_editora["values"] = editoras
        self.combo_editora.current(0)

    def load_comics(self):
        self.rows = get_all_comics()
        self.display_rows(self.rows)

    def apply_filters(self):
        titulo = self.entry_titulo.get().strip()
        edicao = self.entry_edicao.get().strip()
        edicao = int(edicao) if edicao.isdigit() else None
        serie = self.combo_serie.get()
        arco = self.combo_arco.get()
        editora = self.combo_editora.get()

        self.rows = get_comics_by_filters(titulo, edicao, serie, arco, editora)
        self.display_rows(self.rows)

    def clear_filters(self):
        self.entry_titulo.delete(0, tk.END)
        self.entry_edicao.delete(0, tk.END)
        self.combo_serie.current(0)
        self.combo_arco.current(0)
        self.combo_editora.current(0)
        self.load_comics()

    def display_rows(self, rows):
        for i in self.tree.get_children():
            self.tree.delete(i)

        for row in rows:
            stars = rating_to_stars(row[7])
            display_row = row[:7] + (stars,)
            self.tree.insert("", tk.END, values=display_row)

    def sort_column(self, col, reverse):
        col_index = self.cols.index(col)
        try:
            sorted_rows = sorted(self.rows, key=lambda x: (x[col_index] is None, x[col_index]), reverse=reverse)
        except TypeError:
            sorted_rows = sorted(self.rows, key=lambda x: str(x[col_index]), reverse=reverse)
        self.display_rows(sorted_rows)
        self.sort_orders[col] = not reverse
        self.tree.heading(col, command=lambda c=col: self.sort_column(c, self.sort_orders[col]))

    def on_double_click(self, event):
        item = self.tree.selection()
        if not item:
            return
        comic_id = self.tree.item(item, "values")[0]
        EditComicWindow(self.master, comic_id, refresh_func=self.load_comics)

    def voltar(self):
        self.master.destroy()
        if self.back_func:
            self.back_func()

    def open_dashboard(self):
        popup = tk.Toplevel(self.master)
        popup.title("Dashboard")
        popup.iconbitmap(ICON_PATH)
        tk.Label(popup, text="Abrindo o dashboard...").pack(padx=20, pady=20)
        popup.update()
        os.startfile(DASHBOARD_PATH)
        popup.after(1000, popup.destroy)
