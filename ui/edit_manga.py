import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from db.queries import get_manga_by_id, update_manga, delete_manga_by_id
from utils.helpers import stars_display
from utils.validators import validate_reading_date, validate_rating


class EditMangaWindow:
    def __init__(self, master, manga_id, refresh_func=None):
        self.master = tk.Toplevel(master)
        self.master.title("Editar Mangá")
        self.manga_id = manga_id
        self.refresh_func = refresh_func

        # Carrega dados do mangá com série e autor
        manga = get_manga_by_id(manga_id)
        if not manga:
            messagebox.showerror("Erro", "Mangá não encontrado!")
            self.master.destroy()
            return

        self.series_name = manga[4]       # MangaSeries.name
        self.author = manga[5]            # MangaSeries.author
        self.volume = manga[1]            # volume
        self.reading_date_val = manga[2]  # reading_date
        self.rating_val = manga[3]        # rating

        self.create_widgets()
        self.master.grab_set()

    def create_widgets(self):
        # Série, Autor e Volume
        tk.Label(self.master, text=f"Série: {self.series_name}").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        tk.Label(self.master, text=f"Autor: {self.author}").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        tk.Label(self.master, text=f"Volume: {self.volume}").grid(row=2, column=0, sticky="w", padx=5, pady=5)

        # Data de leitura
        tk.Label(self.master, text="Data de Leitura (opcional):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.date_entry = DateEntry(self.master, width=12, background='purple', foreground='red', borderwidth=2, year=2025)
        self.date_entry.grid(row=3, column=1, padx=5, pady=5)
        if self.reading_date_val:
            dt = validate_reading_date(self.reading_date_val)
            if dt:
                self.date_entry.set_date(dt)

        # Avaliação (estrelas)
        tk.Label(self.master, text="Avaliação:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.rating_var = tk.IntVar(value=self.rating_val or 0)
        stars_frame = tk.Frame(self.master)
        stars_frame.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        self.stars = []
        for i, char in enumerate(stars_display(self.rating_var.get()), start=1):
            lbl = tk.Label(stars_frame, text=char, font=("Arial", 18), fg="gold" if char == "★" else "gray")
            lbl.grid(row=0, column=i, padx=2)
            lbl.bind("<Button-1>", lambda e, n=i: self.set_stars(n))
            self.stars.append(lbl)

        # Botões
        tk.Button(self.master, text="Salvar Alterações", command=self.save_changes).grid(row=5, column=0, columnspan=2, pady=5)
        tk.Button(self.master, text="🗑 Excluir", fg="red", command=self.delete_manga).grid(row=6, column=0, columnspan=2, pady=5)

    # Controle de estrelas
    def set_stars(self, n):
        self.rating_var.set(n)
        for lbl, char in zip(self.stars, stars_display(n)):
            lbl.config(text=char, fg="gold" if char == "★" else "gray")

    # Salvar alterações
    def save_changes(self):
        reading_date = validate_reading_date(self.date_entry.get())
        if self.date_entry.get().strip() and reading_date is None:
            messagebox.showerror("Erro", "Data de leitura inválida!")
            return

        rating = validate_rating(self.rating_var.get())

        try:
            update_manga(self.manga_id, reading_date, rating)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao atualizar mangá:\n{e}")
            return

        messagebox.showinfo("Sucesso", "Mangá atualizado!")
        if self.refresh_func:
            self.refresh_func()
        self.master.destroy()

    # Excluir mangá
    def delete_manga(self):
        if messagebox.askyesno("Confirmação", "Tem certeza que deseja excluir este mangá?"):
            try:
                delete_manga_by_id(self.manga_id)
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao excluir mangá:\n{e}")
                return
            messagebox.showinfo("Sucesso", "Mangá excluído com sucesso!")
            if self.refresh_func:
                self.refresh_func()
            self.master.destroy()
