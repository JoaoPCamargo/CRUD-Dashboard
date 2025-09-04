import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from db.queries import (
    get_filter_options,
    get_comics_by_filters,
    get_mangas_by_filters,
    get_manga_series,
    get_manga_authors
)
from config import ICON_PATH
from utils.validators import validate_int
from utils.helpers import rating_to_stars
from ui.edit_comic import EditComicWindow
from ui.edit_manga import EditMangaWindow
from ui.dashboard.main import DashboardMain


class CollectionConsult:
    def __init__(self, master, back_func):
        self.master = master
        self.back_func = back_func
        self.tipo = "comic"  # padrão

        self.setup_window()
        self.setup_filters()
        self.setup_treeview()
        self.load_filter_options()
        self.apply_filters()

    # ---------------- SETUP ----------------
    def setup_window(self):
        self.master.title("Consultar Coleção (Quadrinhos / Mangás)")
        self.master.iconbitmap(ICON_PATH)
        self.master.geometry("950x500")

        btn_frame = tk.Frame(self.master)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Voltar", command=self.voltar).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(btn_frame, text="📊", width=3, command=self.open_dashboard).pack(side=tk.LEFT)

    def setup_filters(self):
        filtros_frame = ttk.LabelFrame(self.master, text="Filtros")
        filtros_frame.pack(fill="x", padx=10, pady=5)

        # Título e Edição
        tk.Label(filtros_frame, text="Título:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_titulo = tk.Entry(filtros_frame, width=25)
        self.entry_titulo.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(filtros_frame, text="Edição/Volume:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        vcmd = self.master.register(validate_int)
        self.entry_edicao = tk.Entry(filtros_frame, width=10, validate="key", validatecommand=(vcmd, "%P"))
        self.entry_edicao.grid(row=0, column=3, padx=5, pady=5)

        # Série, Arco, Editora
        tk.Label(filtros_frame, text="Série:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.combo_serie = ttk.Combobox(filtros_frame, state="readonly", width=25)
        self.combo_serie.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(filtros_frame, text="Arco:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.combo_arco = ttk.Combobox(filtros_frame, state="readonly", width=25)
        self.combo_arco.grid(row=1, column=3, padx=5, pady=5)

        tk.Label(filtros_frame, text="Editora:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.combo_editora = ttk.Combobox(filtros_frame, state="readonly", width=25)
        self.combo_editora.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(filtros_frame, text="Autor:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.combo_autor = ttk.Combobox(filtros_frame, state="readonly", width=25)
        self.combo_autor.grid(row=2, column=3, padx=5, pady=5)
        self.combo_autor["values"] = ["Todos"]
        self.combo_autor.set("Todos")

        # Tipo: Quadrinho / Mangá
        tk.Label(filtros_frame, text="Tipo:").grid(row=4, column=0, sticky="w")
        self.is_comic_var = tk.BooleanVar(value=True)
        self.is_manga_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(filtros_frame, text="Quadrinho", variable=self.is_comic_var,
                        command=lambda: self.toggle_type("comic")).grid(row=4, column=1, sticky="w")
        ttk.Checkbutton(filtros_frame, text="Mangá", variable=self.is_manga_var,
                        command=lambda: self.toggle_type("manga")).grid(row=4, column=2, sticky="w")

        # Botões de ação
        ttk.Button(filtros_frame, text="Pesquisar", command=self.apply_filters).grid(row=5, column=0, columnspan=2, pady=8)
        ttk.Button(filtros_frame, text="Limpar Filtros", command=self.clear_filters).grid(row=5, column=2, columnspan=2, pady=8)

    def setup_treeview(self):
        self.tree = ttk.Treeview(self.master, show="headings")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.sort_orders = {}

    # ---------------- FILTERS ----------------
    def toggle_type(self, tipo):
        """Alterna entre Quadrinho e Mangá e atualiza comboboxes."""
        if tipo == "comic":
            self.is_comic_var.set(True)
            self.is_manga_var.set(False)
            series, arcos, editoras = get_filter_options()
            self.combo_serie["values"] = ["Todas"] + series if series else ["Todas"]
            self.combo_serie.set("Todas")
            self.combo_arco["values"] = ["Todos"] + arcos if arcos else ["Todos"]
            self.combo_arco.set("Todos")
            self.combo_editora["values"] = ["Todas"] + editoras if editoras else ["Todas"]
            self.combo_editora.set("Todas")
            self.combo_autor["values"] = ["Todos"]
            self.combo_autor.set("Todos")
        else:
            self.is_comic_var.set(False)
            self.is_manga_var.set(True)
            mangas = get_manga_series()
            authors = get_manga_authors()
            self.combo_serie["values"] = ["Todas"] + mangas if mangas else ["Todas"]
            self.combo_serie.set("Todas")
            self.combo_arco["values"] = []
            self.combo_arco.set("")
            self.combo_editora["values"] = []
            self.combo_editora.set("")
            self.combo_autor["values"] = ["Todos"] + authors if authors else ["Todos"]
            self.combo_autor.set("Todos")

    def apply_filters(self):
        """Aplica os filtros selecionados e atualiza a Treeview."""
        titulo = self.entry_titulo.get().strip() or None
        edicao = self.entry_edicao.get().strip()
        edicao = int(edicao) if edicao.isdigit() else None
        serie = self.combo_serie.get()
        arco = self.combo_arco.get()
        editora = self.combo_editora.get()

        if self.is_comic_var.get():
            self.tipo = "comic"
            serie_val = None if serie in ("Todas", "") else serie
            arco_val = None if arco in ("Todos", "") else arco
            editora_val = None if editora in ("Todas", "") else editora
            self.rows = get_comics_by_filters(titulo, edicao, serie_val, arco_val, editora_val) or []
        else:
            self.tipo = "manga"
            serie_val = None if serie in ("Todas", "") else serie
            author_val = None if self.combo_autor.get() in ("Todos", "") else self.combo_autor.get()
            self.rows = get_mangas_by_filters(titulo, edicao, serie_val, author_val) or []

        self.display_rows(self.rows)

    def load_filter_options(self):
        if self.is_comic_var.get():
            series, arcos, editoras = get_filter_options()
            self.combo_serie["values"] = series
            self.combo_arco["values"] = arcos
            self.combo_editora["values"] = editoras
            if series: self.combo_serie.current(0)
            if arcos: self.combo_arco.current(0)
            if editoras: self.combo_editora.current(0)
        else:
            mangas = get_manga_series()
            self.combo_serie["values"] = mangas
            self.combo_arco["values"] = []
            self.combo_editora["values"] = []
            if mangas: self.combo_serie.current(0)
            self.combo_arco.set("")
            self.combo_editora.set("")

    # ---------------- DISPLAY ----------------
    def display_rows(self, rows):
        for i in self.tree.get_children():
            self.tree.delete(i)

        if self.tipo == "comic":
            cols = ("ID", "Título", "Edição", "Data de Leitura", "Editora", "Série", "Arco", "Avaliação")
        else:
            cols = ("ID", "Volume", "Data de Leitura", "Série", "Autor", "Avaliação")

        self.tree["columns"] = cols
        self.cols = cols
        self.sort_orders = {col: False for col in cols}

        for col in cols:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c, False))
            self.tree.column(col, width=120)

        for row in rows:
            stars = rating_to_stars(row[-1])
            display_row = row[:-1] + (stars,)
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

    # ---------------- DOUBLE CLICK ----------------
    def on_double_click(self, event):
        item = self.tree.selection()
        if not item:
            return
        row_id = self.tree.item(item, "values")[0]
        if self.tipo == "comic":
            EditComicWindow(self.master, row_id, refresh_func=self.apply_filters)
        else:
            EditMangaWindow(self.master, row_id, refresh_func=self.apply_filters)

    # ---------------- NAVIGATION ----------------
    def voltar(self):
        self.master.destroy()
        if self.back_func:
            self.back_func()

    def open_dashboard(self):
        dash_window = tk.Toplevel(self.master)
        dash_window.title("Dashboard")
        dash_window.iconbitmap(ICON_PATH)

        dashboard = DashboardMain(dash_window, back_func=lambda: self.back(dash_window))
        dashboard.pack(fill="both", expand=True)

        def on_close():
            plt.close('all')  # fecha todas as figuras matplotlib
            for child in dashboard.winfo_children():
                child.destroy()
            dash_window.destroy()

        dash_window.protocol("WM_DELETE_WINDOW", on_close)

    def clear_filters(self):
        self.entry_titulo.delete(0, tk.END)
        self.entry_edicao.delete(0, tk.END)

        if self.is_comic_var.get():
            if self.combo_serie["values"]: self.combo_serie.current(0)
            if self.combo_arco["values"]: self.combo_arco.current(0)
            if self.combo_editora["values"]: self.combo_editora.current(0)
        else:
            self.combo_serie.set("Todas")
            self.combo_arco.set("")
            self.combo_editora.set("")
            self.combo_autor.set("Todos")

        self.is_comic_var.set(True)
        self.is_manga_var.set(False)
        self.tipo = "comic"
        self.apply_filters()
