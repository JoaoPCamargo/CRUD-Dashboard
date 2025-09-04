import tkinter as tk
import matplotlib.pyplot as plt
from utils.helpers import load_random_image_from_folder, resize_image_for_canvas, create_outlined_text, create_canvas_button
from utils.validators import validate_image_folder
from ui.comic_add import ComicAdd
from ui.manga_add import MangaAdd
from ui.collection_consult import CollectionConsult
from ui.library_browser import LibraryBrowser
from ui.cbr_reader import CBRReader
from config import ICON_PATH, BACKGROUND_PATH
from ui.dashboard.main import DashboardMain

class MainMenu:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Menu Principal")
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.root.iconbitmap(ICON_PATH)
        self.root.geometry("500x400")

        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.bg_folder = BACKGROUND_PATH
        self.bg_files = validate_image_folder(self.bg_folder)

        self.bg_image = load_random_image_from_folder(self.bg_folder)
        self.bg_photo = None
        self.bg_canvas_image = None

        # --- textos ---
        self.title_text_items = create_outlined_text(self.canvas, "Bem-vindo ao Chronica Verse", 16, bold=True)
        self.subtitle_text_items = create_outlined_text(self.canvas, "Seu Catálogo de Quadrinhos", 12, italic=True)

        # --- botões ---
        self.buttons = []
        # Botões grandes
        self.buttons.append(create_canvas_button(self.canvas, "Adicionar Quadrinho", self.open_add))
        self.buttons.append(create_canvas_button(self.canvas, "Adicionar Mangá", self.open_add_manga))
        self.buttons.append(create_canvas_button(self.canvas, "Consultar Coleção", self.open_consult))
        self.buttons.append(create_canvas_button(self.canvas, "Biblioteca", self.open_library))
        # Botões pequenos
        self.buttons.append(create_canvas_button(self.canvas, "📖", self.open_reader, width=50, square=True))
        self.buttons.append(create_canvas_button(self.canvas, "📊", self.open_dashboard, width=50, square=True))

        self.root.bind("<Configure>", self.on_resize)
        self.root.after(100, self.resize_bg)

        self.root.mainloop()

    # ------------------- RESIZE -------------------
    def resize_bg(self, event=None):
        w, h = self.root.winfo_width(), self.root.winfo_height()
        if w < 10 or h < 10:
            return

        # --- fundo ---
        self.bg_photo = resize_image_for_canvas(self.bg_image, w, h)
        if not self.bg_canvas_image:
            self.bg_canvas_image = self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
        else:
            self.canvas.itemconfig(self.bg_canvas_image, image=self.bg_photo)
        self.canvas.tag_lower(self.bg_canvas_image)

        # --- textos ---
        for items in [self.title_text_items, self.subtitle_text_items]:
            for item_id, dx, dy in items:
                y_pos = h*0.1 if items == self.title_text_items else h*0.2
                self.canvas.coords(item_id, w/2+dx, y_pos+dy)

        # --- botões grandes (dinâmico) ---
        large_buttons = self.buttons[:4]  # os primeiros 4 são grandes
        num_large = len(large_buttons)
        spacing = 60
        y_start = h*0.35
        for i, btn in enumerate(large_buttons):
            btn_width = btn.get('width', 150)
            btn_height = btn.get('height', 40)
            x0 = w/2 - btn_width/2
            y0 = y_start + i*spacing - btn_height/2
            x1 = w/2 + btn_width/2
            y1 = y_start + i*spacing + btn_height/2
            self.canvas.coords(btn['rect'], x0, y0, x1, y1)
            self.canvas.coords(btn['text'], w/2, y_start + i*spacing)

        # --- botões pequenos (canto inferior direito) ---
        small_buttons = self.buttons[4:]
        margin_x = 10
        margin_y = 10
        btn_spacing = 55
        for i, btn in enumerate(small_buttons):
            btn_width = btn.get('width', 40)
            btn_height = btn.get('height', 40)
            x0 = w - margin_x - btn_width
            y0 = h - margin_y - (i+1)*btn_spacing
            x1 = w - margin_x
            y1 = h - margin_y - i*btn_spacing
            self.canvas.coords(btn['rect'], x0, y0, x1, y1)
            self.canvas.coords(btn['text'], (x0+x1)/2, (y0+y1)/2)

    def on_resize(self, event):
        self.resize_bg()

    # ------------------- JANELAS -------------------
    def open_add(self):
        self.root.withdraw()
        add_window = tk.Toplevel()
        add_window.protocol("WM_DELETE_WINDOW", self.quit_app)
        app = ComicAdd(add_window)
        app.set_back_func(lambda: self.back(add_window))

    def open_add_manga(self):
        self.root.withdraw()
        manga_window = tk.Toplevel()
        manga_window.protocol("WM_DELETE_WINDOW", self.quit_app)
        app = MangaAdd(manga_window)
        app.set_back_func(lambda: self.back(manga_window))

    def open_consult(self):
        self.root.withdraw()
        consult_window = tk.Toplevel()
        consult_window.protocol("WM_DELETE_WINDOW", self.quit_app)
        CollectionConsult(consult_window, back_func=lambda: self.back(consult_window))

    def open_library(self):
        self.root.withdraw()
        lib_window = tk.Toplevel()
        lib_window.protocol("WM_DELETE_WINDOW", self.quit_app)
        LibraryBrowser(lib_window, back_to_main_func=self.back)

    def open_reader(self):
        self.root.withdraw()
        reader_window = tk.Toplevel()
        reader_window.protocol("WM_DELETE_WINDOW", self.quit_app)
        CBRReader(master=reader_window, back_func=lambda: self.back(reader_window))

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

    def quit_app(self):
        self.root.destroy()

    def back(self, win):
        win.destroy()
        self.root.deiconify()
