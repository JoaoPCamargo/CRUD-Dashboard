import sqlite3
import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from tkcalendar import DateEntry
from ui.comic_add import ComicAdd
from ui.comic_consult import ComicConsult
from ui.edit_comic import EditComicWindow
from config import DB_PATH, DASHBOARD_PATH, ICON_PATH

class MainMenu:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Menu Principal")
        self.root.iconbitmap(ICON_PATH)
        self.root.geometry("300x200")

        # Título principal
        tk.Label(self.root, text="Bem-vindo ao Chronica Verse", font=("Arial", 16, "bold")).pack(pady=(10, 2))

        # Subtítulo
        tk.Label(self.root, text="Seu Catálogo de Quadrinhos", font=("Arial", 12, "italic")).pack(pady=(0, 10))


        tk.Button(self.root, text="Adicionar Quadrinho", width=20, command=self.open_add).pack(pady=5)
        tk.Button(self.root, text="Consultar Quadrinhos", width=20, command=self.open_consult).pack(pady=5)

        dash_btn = tk.Button(self.root, text="📊", width=3, command=self.open_dashboard)
        dash_btn.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

        self.root.mainloop()

    def open_add(self):
        self.root.withdraw()  # esconde o menu
        add_window = tk.Toplevel()
        app = ComicAdd(add_window)  # chama o formulário principal
        app.set_back_func(lambda: self.back(add_window))

    def open_consult(self):
        self.root.withdraw()
        consult_window = tk.Toplevel()
        ComicConsult(consult_window, back_func=lambda: self.back(consult_window))

    def open_dashboard(self):
        popup = tk.Toplevel(self.root)
        popup.title("Dashboard")
        popup.iconbitmap(ICON_PATH)
        label = tk.Label(popup, text="Abrindo o dashboard...")
        label.pack(padx=20, pady=20)
        popup.update()
        os.startfile(DASHBOARD_PATH)
        popup.after(1000, popup.destroy)

    def back(self, win):
        win.destroy()
        self.root.deiconify()  # mostra o menu novamente