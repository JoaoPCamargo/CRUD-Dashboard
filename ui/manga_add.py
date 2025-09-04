import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from ui.dashboard.main import DashboardMain
from db.queries import get_manga_series, insert_manga_volumes, insert_manga_series
from config import ICON_PATH
from utils import validators as v
from utils import helpers as h


class MangaAdd:
    def __init__(self, root):
        self.root = root
        self.root.title("Cadastro de Mangás")
        self.root.iconbitmap(ICON_PATH)

        # --- SÉRIE ---
        tk.Label(root, text="Série:").grid(row=0, column=0, sticky="w")
        self.series_cb = ttk.Combobox(root, state="readonly")
        self.series_cb.grid(row=0, column=1, padx=5, pady=5)
        self.add_series_btn = tk.Button(root, text="+", command=self.add_series)
        self.add_series_btn.grid(row=0, column=2, padx=5)

        # --- VOLUMES ---
        tk.Label(root, text="Volumes (ex: 1,2,3,5-10):").grid(row=1, column=0, sticky="w")
        self.volumes_entry = tk.Entry(root)
        self.volumes_entry.grid(row=1, column=1, padx=5, pady=5)

        # --- DATA DE LEITURA (opcional) ---
        tk.Label(root, text="Data de Leitura:").grid(row=2, column=0, sticky="w")
        self.date_entry = DateEntry(root, width=12, background='purple', foreground='red',
                                    borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)
        self.date_entry.delete(0, tk.END)

        # --- AVALIAÇÃO ---
        tk.Label(root, text="Avaliação:").grid(row=3, column=0, sticky="w")
        self.avaliacao_var = tk.IntVar(value=0)
        stars_frame = tk.Frame(root)
        stars_frame.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.stars = []
        for i in range(1, 6):
            lbl = tk.Label(stars_frame, text="☆", font=("Arial", 18))
            lbl.grid(row=0, column=i, padx=2)
            lbl.bind("<Button-1>", lambda e, n=i: self.set_stars(n))
            self.stars.append(lbl)

        # --- BOTÕES ---
        self.save_btn = tk.Button(root, text="Cadastrar", command=self.save_volumes)
        self.save_btn.grid(row=4, column=0, padx=5, pady=10)
        self.back_btn = tk.Button(root, text="Voltar", command=self.back_to_menu)
        self.back_btn.grid(row=4, column=2, padx=5, pady=10)
        self.dash_btn = tk.Button(root, text="📊", width=3, command=self.open_dashboard)
        self.dash_btn.grid(row=4, column=1, padx=5, pady=10, sticky="w")

        # --- CARREGA SERIES ---
        self.load_series()

    def open_dashboard(self):
        dash_window = tk.Toplevel(self.root)
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
    # ---------------- LOADERS ----------------
    def load_series(self):
        self.series_list = get_manga_series()
        self.series_cb["values"] = [s[1] for s in self.series_list]

    # ---------------- ADD SERIES ----------------
    def add_series(self):
        win = tk.Toplevel(self.root)
        win.title("Nova Série")
        win.iconbitmap(ICON_PATH)

        # --- Campos ---
        tk.Label(win, text="Nome da Série:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        entry_name = tk.Entry(win)
        entry_name.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(win, text="Autor:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        entry_author = tk.Entry(win)
        entry_author.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(win, text="Total de Volumes:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        entry_total = tk.Entry(win)
        entry_total.grid(row=2, column=1, padx=10, pady=5)

        def salvar():
            nome = entry_name.get().strip()
            autor = entry_author.get().strip()
            total_volumes = v.to_int_or_none(entry_total.get())

            if not v.is_non_empty(nome):
                messagebox.showerror("Erro", "Nome da série não pode ser vazio!", parent=win)
                return
            if not v.is_non_empty(autor):
                messagebox.showerror("Erro", "Autor não pode ser vazio!", parent=win)
                return

            try:
                insert_manga_series(nome, autor, total_volumes)
                self.load_series()
                messagebox.showinfo("Sucesso", "Série adicionada!", parent=win)
                win.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao adicionar série: {e}", parent=win)

        tk.Button(win, text="Salvar", command=salvar).grid(row=3, column=0, columnspan=2, pady=10)

    # ---------------- SAVE VOLUMES ----------------
    def save_volumes(self):
        series_idx = self.series_cb.current()
        if series_idx < 0:
            messagebox.showerror("Erro", "Selecione uma série!")
            return
        series_id = self.series_list[series_idx][0]

        volumes_text = self.volumes_entry.get().strip()
        if not volumes_text:
            messagebox.showerror("Erro", "Informe pelo menos um volume!")
            return

        try:
            volumes = h.parse_volumes(volumes_text)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar volumes: {e}")
            return

        date_str = self.date_entry.get().strip()
        reading_date = None
        if date_str:
            try:
                reading_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if v.is_future_date(reading_date):
                    messagebox.showerror("Erro", "A data de leitura não pode ser no futuro!")
                    return
            except ValueError:
                messagebox.showerror("Erro", "Data inválida! Use o formato yyyy-mm-dd")
                return

        avaliacao = self.avaliacao_var.get() or None

        try:
            insert_manga_volumes(series_id, volumes, reading_date, avaliacao)
            messagebox.showinfo("Sucesso", f"{len(volumes)} volumes cadastrados!")
            h.clear_entries(self.volumes_entry, self.date_entry)
            self.series_cb.set("")
            self.avaliacao_var.set(0)
            self.set_stars(0)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar volumes: {e}")

    # ---------------- AVALIAÇÃO ----------------
    def set_stars(self, n):
        self.avaliacao_var.set(n)
        stars = h.stars_display(n)
        for lbl, star in zip(self.stars, stars):
            lbl.config(text=star, fg="gold" if star == "★" else "gray")

    # ---------------- VOLTAR AO MENU ----------------
    def set_back_func(self, func):
        self.back_func = func

    def back_to_menu(self):
        if hasattr(self, 'back_func') and callable(self.back_func):
            self.back_func()
        else:
            self.root.destroy()