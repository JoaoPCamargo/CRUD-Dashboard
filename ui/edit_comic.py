import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from config import ICON_PATH
from db.queries import (
    get_comic_by_id, update_comic,
    get_publishers, get_series, get_arcs, get_comic_publisher)
from utils.helpers import stars_display, find_index_by_id
from utils.validators import validate_issue, validate_reading_date, validate_rating

class EditComicWindow:
    def __init__(self, master, comic_id, refresh_func=None):
        self.master = tk.Toplevel(master)
        self.master.title("Editar Quadrinho")
        self.master.iconbitmap(ICON_PATH)
        self.comic_id = comic_id
        self.refresh_func = refresh_func

        # Carregar dados do quadrinho
        row = get_comic_by_id(self.comic_id)
        if not row:
            messagebox.showerror("Erro", "Quadrinho não encontrado!")
            self.master.destroy()
            return

        self.title_val, self.issue_val, self.date_val, self.series_id_val, self.arc_id_val, self.rating_val = row

        self.create_widgets()
        self.load_publishers_series_arcs()
        self.master.grab_set()

    # --- Criação dos widgets ---
    def create_widgets(self):
        # Título
        tk.Label(self.master, text="Título:").grid(row=0, column=0, sticky="w")
        self.title_entry = tk.Entry(self.master, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)
        self.title_entry.insert(0, self.title_val or "")

        # Número da edição
        tk.Label(self.master, text="Número da Edição:").grid(row=1, column=0, sticky="w")
        self.issue_entry = tk.Entry(self.master, width=10)
        self.issue_entry.grid(row=1, column=1, padx=5, pady=5)
        self.issue_entry.insert(0, str(self.issue_val))

        # Data de leitura
        tk.Label(self.master, text="Data de Leitura (opcional):").grid(row=2, column=0, sticky="w")
        self.date_entry = DateEntry(self.master, width=12, background='purple', foreground='red', borderwidth=2, year=2025)
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)
        if self.date_val:
            dt = validate_reading_date(self.date_val)
            if dt:
                self.date_entry.set_date(dt)

        # Combos
        tk.Label(self.master, text="Editora:").grid(row=3, column=0, sticky="w")
        self.combo_editora = ttk.Combobox(self.master, state="readonly", width=25)
        self.combo_editora.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(self.master, text="Série:").grid(row=4, column=0, sticky="w")
        self.combo_serie = ttk.Combobox(self.master, state="readonly", width=25)
        self.combo_serie.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(self.master, text="Arco:").grid(row=5, column=0, sticky="w")
        self.combo_arco = ttk.Combobox(self.master, state="readonly", width=25)
        self.combo_arco.grid(row=5, column=1, padx=5, pady=5)

        # Avaliação (estrelas)
        tk.Label(self.master, text="Avaliação:").grid(row=6, column=0, sticky="w")
        self.rating_var = tk.IntVar(value=self.rating_val or 0)
        stars_frame = tk.Frame(self.master)
        stars_frame.grid(row=6, column=1, padx=5, pady=5, sticky="w")
        self.stars = []
        for i, char in enumerate(stars_display(self.rating_var.get()), start=1):
            lbl = tk.Label(stars_frame, text=char, font=("Arial", 18), fg="gold" if char == "★" else "gray")
            lbl.grid(row=0, column=i, padx=2)
            lbl.bind("<Button-1>", lambda e, n=i: self.set_stars(n))
            self.stars.append(lbl)

        # Botão salvar
        tk.Button(self.master, text="Salvar Alterações", command=self.save_changes).grid(row=7, column=0, columnspan=2, pady=5)

        # Botão excluir (lixeira)
        tk.Button(self.master, text="🗑", fg="red", command=self.delete_comic).grid(row=7, column=1, columnspan=2, pady=5)


    # --- Controle de estrelas ---
    def set_stars(self, n):
        self.rating_var.set(n)
        for lbl, char in zip(self.stars, stars_display(n)):
            lbl.config(text=char, fg="gold" if char == "★" else "gray")

    # --- Carregar editoras, séries e arcos ---
    def load_publishers_series_arcs(self):
        self.publishers = get_publishers()
        self.combo_editora["values"] = [p[1] for p in self.publishers]
        pub_id = get_comic_publisher(self.comic_id)
        self.combo_editora.current(find_index_by_id(self.publishers, pub_id))

        self.series = get_series()
        self.combo_serie["values"] = [s[1] for s in self.series]
        self.combo_serie.current(find_index_by_id(self.series, self.series_id_val))

        self.arcs = get_arcs()
        self.combo_arco["values"] = [a[1] for a in self.arcs]
        if self.arc_id_val:
            self.combo_arco.current(find_index_by_id(self.arcs, self.arc_id_val))
        else:
            self.combo_arco.set('')

    # --- Salvar alterações ---
    def save_changes(self):
        title = self.title_entry.get().strip()
        
        # Número da edição
        issue = validate_issue(self.issue_entry.get())
        if issue is None:
            messagebox.showerror("Erro", "Número da edição inválido!")
            return

        # Data de leitura
        reading_date = validate_reading_date(self.date_entry.get())
        if self.date_entry.get().strip() and reading_date is None:
            messagebox.showerror("Erro", "Data de leitura inválida!")
            return

        # Série e arco
        series_idx = self.combo_serie.current()
        series_id = self.series[series_idx][0] if series_idx >= 0 else None

        arc_idx = self.combo_arco.current()
        arc_id = self.arcs[arc_idx][0] if arc_idx >= 0 else None

        # Avaliação
        rating = validate_rating(self.rating_var.get())

        # Atualizar banco
        update_comic(self.comic_id, title or None, issue, reading_date, series_id, arc_id, rating)

        messagebox.showinfo("Sucesso", "Quadrinho atualizado!")
        if self.refresh_func:
            self.refresh_func()
        self.master.destroy()

    def delete_comic(self):
        answer = messagebox.askyesno("Confirmação", "Tem certeza que deseja excluir este quadrinho?")
        if answer:
            from db.queries import delete_comic_by_id
            delete_comic_by_id(self.comic_id)
            messagebox.showinfo("Sucesso", "Quadrinho excluído com sucesso!")
            if self.refresh_func:
                self.refresh_func()
            self.master.destroy()
