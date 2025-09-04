import tkinter as tk
from tkinter import filedialog, Canvas, Frame, Label, Button, Scrollbar
from PIL import Image, ImageTk
import threading
import os
import rarfile
from ui.cbr_reader import CBRReader
from config import FOLDER_EMPTY_PATH, FOLDER_CBR_PATH, ICON_PATH
from utils.helpers import next_column, clear_history
from utils.validators import is_valid_folder, is_image_file

class LibraryBrowser:
    def __init__(self, master, back_to_main_func):
        self.master = master
        self.master.title("Biblioteca")
        self.master.iconbitmap(ICON_PATH)
        self.master.geometry("800x400")

        self.history = []
        self.current_path = None
        self.back_to_main_func = back_to_main_func

        # Ícones
        self.folder_empty_icon = ImageTk.PhotoImage(Image.open(FOLDER_EMPTY_PATH).resize((120, 120)))
        self.folder_cbr_icon = ImageTk.PhotoImage(Image.open(FOLDER_CBR_PATH).resize((120, 120)))

        # Botões
        buttons_frame = Frame(master)
        buttons_frame.pack(pady=5)
        self.select_folder_btn = Button(buttons_frame, text="Selecionar Pasta", command=self.select_folder)
        self.select_folder_btn.pack(side="left", padx=5)
        self.main_menu_btn = Button(buttons_frame, text="Voltar", command=self.back)
        self.main_menu_btn.pack(side="left", padx=5)

        # Canvas e scroll
        self.canvas = Canvas(master, bg="white")
        self.scroll_y = Scrollbar(master, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll_y.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.bind_mousewheel(self.canvas)

        # Frame interno
        self.inner_frame = Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.inner_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", lambda e: self.redraw_level())

        # Tenta carregar a última pasta
        last_folder = self.load_last_folder()
        if last_folder:
            self.load_level(last_folder)

    # ---------------------- Manipulação de pastas ----------------------
    def save_last_folder(self, folder_path):
        try:
            with open("last_folder.txt", "w") as f:
                f.write(folder_path)
        except Exception as e:
            print(f"Erro ao salvar pasta: {e}")

    def load_last_folder(self):
        try:
            with open("last_folder.txt", "r") as f:
                folder = f.read().strip()
                if is_valid_folder(folder):
                    return folder
        except Exception as e:
            print(f"Erro ao carregar pasta salva: {e}")
        return None

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            clear_history(self.history)
            self.current_path = folder
            self.save_last_folder(folder)
            self.load_level(folder)

    # ---------------------- Carregamento da biblioteca ----------------------
    def load_level(self, path):
        if not is_valid_folder(path):
            return
        self.current_path = path

        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        items = os.listdir(path)
        folders = sorted([f for f in items if os.path.isdir(os.path.join(path, f))])
        cbr_files = sorted([f for f in items if f.lower().endswith(".cbr")])

        row, padding, lombada_width, lombada_height = 0, 5, 20, 120
        available_width = self.canvas.winfo_width() or 800
        max_cols = max(1, available_width // (lombada_width + padding))

        # Arquivos .cbr da pasta principal
        if cbr_files:
            col = 1
            folder_frame = Frame(self.inner_frame, width=180, height=lombada_height, bg="white")
            folder_frame.grid(row=row, column=0, padx=padding, pady=padding, sticky="nw")
            folder_frame.grid_propagate(False)
            Label(folder_frame, image=self.folder_cbr_icon).pack()
            Label(folder_frame, text=os.path.basename(path), bg="white").pack()

            for cbr_file in cbr_files:
                cbr_path = os.path.join(path, cbr_file)
                lbl = Label(self.inner_frame, bg="white")
                lbl.grid(row=row, column=col, padx=padding, pady=padding)
                lbl.full_path = cbr_path
                threading.Thread(target=self.load_lombada, args=(lbl, cbr_path, lombada_width, lombada_height), daemon=True).start()
                lbl.bind("<Double-1>", self.open_cbr)
                row, col = next_column(row, col, max_cols)

        # Pastas
        row += 1
        for f in folders:
            full_path = os.path.join(path, f)
            cbr_files_in_folder = sorted([file for file in os.listdir(full_path) if file.lower().endswith(".cbr")])
            has_cbr = bool(cbr_files_in_folder)

            folder_frame = Frame(self.inner_frame, width=180, height=lombada_height, bg="white")
            folder_frame.grid(row=row, column=0, padx=padding, pady=padding, sticky="nw")
            folder_frame.grid_propagate(False)
            Label(folder_frame, image=self.folder_cbr_icon if has_cbr else self.folder_empty_icon).pack()
            Label(folder_frame, text=f, bg="white").pack()

            col = 1
            for cbr_file in cbr_files_in_folder:
                if col >= max_cols:
                    col = 1
                    row += 1
                cbr_path = os.path.join(full_path, cbr_file)
                lbl = Label(self.inner_frame, bg="white")
                lbl.grid(row=row, column=col, padx=padding, pady=padding)
                lbl.full_path = cbr_path
                threading.Thread(target=self.load_lombada, args=(lbl, cbr_path, lombada_width, lombada_height), daemon=True).start()
                lbl.bind("<Double-1>", self.open_cbr)
                col += 1
            row += 1

        self.inner_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # ---------------------- Carregamento das lombadas ----------------------
    def load_lombada(self, lbl, filepath, w, h):
        cover = self.get_cover(filepath)
        if cover is None:
            cover = Image.new("RGB", (w, h), "gray")
        cover = cover.resize((w, h), Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(cover)
        lbl.after(0, lambda: lbl.config(image=tk_img) if lbl.winfo_exists() else None)
        lbl.image = tk_img

    def get_cover(self, filepath):
        try:
            rf = rarfile.RarFile(filepath)
            image_names = sorted([f for f in rf.namelist() if is_image_file(f)])
            if image_names:
                from PIL import Image
                with rf.open(image_names[0]) as img_file:
                    cover = Image.open(img_file)
                    cover.load()
                    return cover
        except Exception as e:
            print(f"Erro ao gerar capa: {e}")
        return None

    # ---------------------- Rolagem ----------------------
    def bind_mousewheel(self, widget):
        widget.bind_all("<MouseWheel>", self._on_mousewheel)
        widget.bind_all("<Button-4>", self._on_mousewheel)
        widget.bind_all("<Button-5>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    # ---------------------- Abrir CBR ----------------------
    def open_cbr(self, event):
        filepath = event.widget.full_path
        self.master.withdraw()
        reader_window = tk.Toplevel(self.master)
        reader_window.title("Chronica Reader")
        reader = CBRReader(master=reader_window, back_func=lambda: (reader_window.destroy(), self.master.deiconify()))
        threading.Thread(target=lambda: reader.load_cbr_from_file(filepath), daemon=True).start()

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def redraw_level(self):
        if self.current_path:
            self.load_level(self.current_path)

    def back(self):
        self.back_to_main_func(self.master)
