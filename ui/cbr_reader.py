import os
import tempfile
import rarfile
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from config import ICON_PATH

from utils.helpers import center_position, double_page_indices, compute_zoom, resize_images
from utils.validators import is_image_file, is_ctrl_pressed


class CBRReader:
    def __init__(self, master=None, back_func=None):
        self.root = master or tk.Tk()
        self.back_func = back_func
        self.double_page_mode = False
        self.japanese_mode = False

        # ------------------ UI ------------------
        self.info_frame = tk.Frame(self.root, bg="white")

        # contador de páginas
        self.page_label_var = tk.StringVar(value="0 / 0")
        self.page_label = tk.Label(
            self.info_frame,
            textvariable=self.page_label_var,
            font=("Arial", 12),
            bg="white"
        )
        self.page_label.pack(side=tk.LEFT, padx=(0, 5))  # espaço entre contador e nome

        # Nome do arquivo
        self.file_label_var = tk.StringVar(value="")
        self.file_label = tk.Label(
            self.info_frame,
            textvariable=self.file_label_var,
            font=("Arial", 12),
            bg="white"
        )
        self.file_label.pack(side=tk.LEFT)

        # Posiciona o frame no rodapé (inicial)
        self.info_frame.place(x=10, y=self.root.winfo_height() - 30)

        self.root.bind("<Configure>", self.update_page_label_position)

        self.root.title("Chronica Reader")
        self.root.iconbitmap(ICON_PATH)
        self.root.geometry("600x800")

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.main_frame, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.img_on_canvas = self.canvas.create_image(0, 0, anchor="nw", image=None)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        self.scroll_y = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scroll_x = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)

        # atalhos para mudar página
        self.root.bind("<Left>", lambda e: self.change_page(-1))
        self.root.bind("<Right>", lambda e: self.change_page(1))

        self.start_btn = tk.Button(self.canvas, text="📖 Abrir CBR", font=("Arial", 18, "bold"), command=self.open_cbr)
        self.start_btn_window = self.canvas.create_window(300, 400, window=self.start_btn)

        self.footer_frame = tk.Frame(self.root)
        self.footer_frame.pack(side=tk.BOTTOM, pady=2)

        if self.back_func:
            self.btn_back = tk.Button(self.footer_frame, text="Voltar", font=("Arial", 12), command=self.back_to_menu)
            self.btn_back.pack(side=tk.LEFT, padx=10, pady=14)

        self.btn_toggle_pages = tk.Button(self.footer_frame, text="⇆", font=("Arial", 14), command=self.toggle_page_mode)
        self.btn_toggle_pages.pack(side=tk.LEFT, padx=10, pady=1)

        self.btn_toggle_japanese = tk.Button(self.footer_frame, text="🇯🇵", font=("Arial", 14), command=self.toggle_japanese_mode)
        self.btn_toggle_japanese.pack(side=tk.LEFT, padx=10, pady=1)

        self.add_reading_btn = tk.Button(self.footer_frame, text="Marcar Leitura", font=("Arial", 12), command=self.add_reading)
        self.add_reading_btn.pack(side=tk.LEFT, padx=10)
        self.add_reading_btn.pack_forget()

        # ------------------ Dados ------------------
        self.temp_dir = None
        self.images = []
        self.current_page = 0
        self.cbr_filename = ""

        self.zoom_factor = 1.0
        self.base_zoom = 1.0
        self.original_imgs = None

        self.pan_start_x = 0
        self.pan_start_y = 0
        self.is_panning = False

        # ------------------ Eventos ------------------
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel)
        self.canvas.bind("<Button-5>", self.on_mousewheel)
        self.canvas.bind("<ButtonPress-1>", self.start_pan, add="+")
        self.canvas.bind("<B1-Motion>", self.do_pan, add="+")
        self.canvas.bind("<ButtonRelease-1>", self.stop_pan, add="+")
        self.canvas.bind("<Button-1>", self.on_canvas_click, add="+")

        if master is None:
            self.root.mainloop()

    # ------------------ PAN ------------------
    def start_pan(self, event):
        self.pan_start_x = event.x
        self.pan_start_y = event.y
        self.is_panning = True

    def do_pan(self, event):
        if not self.is_panning:
            return

        dx = self.pan_start_x - event.x
        dy = self.pan_start_y - event.y

        scroll_region = self.canvas.bbox(self.img_on_canvas)
        if not scroll_region:
            return

        x0, y0, x1, y1 = scroll_region
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        max_x = max(x1 - x0 - canvas_w, 0)
        max_y = max(y1 - y0 - canvas_h, 0)

        if max_x > 0:
            cur_x = self.canvas.xview()[0] * max_x
            cur_x += dx
            self.canvas.xview_moveto(min(max(cur_x / max_x, 0), 1))

        if max_y > 0:
            cur_y = self.canvas.yview()[0] * max_y
            cur_y += dy
            self.canvas.yview_moveto(min(max(cur_y / max_y, 0), 1))

        self.pan_start_x = event.x
        self.pan_start_y = event.y

    def stop_pan(self, event):
        self.is_panning = False

    # ------------------ CBR ------------------
    def open_cbr(self):
        cbr_path = filedialog.askopenfilename(filetypes=[("Comic Book RAR", "*.cbr")])
        if not cbr_path:
            return
        self.load_cbr_from_file(cbr_path)

    def load_cbr_from_file(self, cbr_path):
        if self.temp_dir:
            self.cleanup()
        self.temp_dir = tempfile.mkdtemp()

        try:
            rf = rarfile.RarFile(cbr_path)
            rf.extractall(self.temp_dir)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível extrair o CBR:\n{e}")
            return

        self.images = self.find_images(self.temp_dir)
        if not self.images:
            messagebox.showerror("Erro", "Nenhuma imagem encontrada no CBR!")
            return

        self.current_page = 0
        self.cbr_filename = os.path.basename(cbr_path)
        self.file_label_var.set(self.cbr_filename)   # atualiza nome no label

        self.canvas.itemconfigure(self.start_btn_window, state="hidden")
        self.show_page()

    def find_images(self, folder):
        return sorted([os.path.join(root, f)
                       for root, _, files in os.walk(folder)
                       for f in files if is_image_file(f)])

    # ------------------ SHOW ------------------
    def show_page(self):
        if not self.images:
            return

        pages_to_show = double_page_indices(self.current_page, len(self.images), self.double_page_mode)
        imgs = [Image.open(self.images[i]) for i in pages_to_show]

        total_width = sum(img.width for img in imgs)
        max_height = max(img.height for img in imgs)

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        self.base_zoom = compute_zoom(total_width, max_height, canvas_w, canvas_h)
        self.zoom_factor = 1.0
        self.original_imgs = imgs
        self.page_label_var.set(f"{self.current_page + 1} / {len(self.images)}")

        if self.current_page == len(self.images) - 1:
            self.add_reading_btn.pack(side=tk.LEFT, padx=10)
        else:
            self.add_reading_btn.pack_forget()

        self.render_page()

    def render_page(self):
        if not self.original_imgs:
            return

        resized, total_width, max_height = resize_images(self.original_imgs, self.base_zoom * self.zoom_factor)

        combined = Image.new("RGB", (total_width, max_height), "black")
        x_offset = 0
        for idx, img in enumerate(self.original_imgs):
            w, h = resized[idx]
            combined.paste(img.resize((w, h), Image.LANCZOS), (x_offset, 0))
            x_offset += w

        self.tk_img = ImageTk.PhotoImage(combined)
        self.canvas.itemconfig(self.img_on_canvas, image=self.tk_img)

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        x_pad, y_pad = center_position(canvas_w, canvas_h, total_width, max_height)

        self.canvas.coords(self.img_on_canvas, x_pad, y_pad)
        self.canvas.config(scrollregion=(0, 0, max(total_width, canvas_w), max(max_height, canvas_h)))

    # ------------------ ZOOM ------------------
    def on_mousewheel(self, event):
        if is_ctrl_pressed(event.state):
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            old_zoom = self.zoom_factor
            step = 0.3  # velocidade do zoom

            if event.num == 4 or event.delta > 0:
                self.zoom_factor += step
            elif event.num == 5 or event.delta < 0:
                self.zoom_factor = max(0.1, self.zoom_factor - step)

            self.render_page()
            scale = self.zoom_factor / old_zoom

            total_width = sum(img.width for img in self.original_imgs) * self.base_zoom * self.zoom_factor
            max_height = max(img.height for img in self.original_imgs) * self.base_zoom * self.zoom_factor
            self.canvas.xview_moveto((x * scale - event.x) / total_width)
            self.canvas.yview_moveto((y * scale - event.y) / max_height)
        else:
            self.change_page(-1 if event.num == 4 or event.delta > 0 else 1)

    # ------------------ PAGINAÇÃO ------------------
    def change_page(self, delta):
        step = 2 if self.double_page_mode else 1
        if self.japanese_mode:
            delta = -delta
        self.current_page += delta * step
        self.current_page = max(0, min(self.current_page, len(self.images) - 1))
        self.show_page()

    # ------------------ LIMPEZA ------------------
    def cleanup(self):
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        self.temp_dir = None
        self.images = []
        self.current_page = 0
        self.cbr_filename = ""
        self.file_label_var.set("")
        self.canvas.itemconfigure(self.start_btn_window, state="normal")
        self.add_reading_btn.pack_forget()
        self.canvas.itemconfig(self.img_on_canvas, image=None)

    # ------------------ BACK ------------------
    def back_to_menu(self):
        self.cleanup()
        if self.back_func:
            self.back_func()
        else:
            self.root.destroy()

    def add_reading(self):
        from ui.comic_add import ComicAdd
        self.root.withdraw()
        add_window = tk.Toplevel()
        app = ComicAdd(add_window)
        app.set_back_func(lambda: self.back(add_window))

    def back(self, win):
        win.destroy()
        self.root.deiconify()

    # ------------------ CLIQUE ------------------
    def on_canvas_click(self, event):
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        margin_x = 0.1 * canvas_w
        margin_y = 0.3 * canvas_h
        top_limit = 0.5 * canvas_h - 0.5 * margin_y
        bottom_limit = 0.5 * canvas_h + 0.5 * margin_y
        if top_limit <= event.y <= bottom_limit:
            if event.x < margin_x:
                self.change_page(-1)
            elif event.x > canvas_w - margin_x:
                self.change_page(1)

    # ------------------ MODOS ------------------
    def toggle_page_mode(self):
        self.double_page_mode = not self.double_page_mode
        self.root.geometry("1000x800" if self.double_page_mode else "600x800")
        self.show_page()

    def toggle_japanese_mode(self):
        self.japanese_mode = not self.japanese_mode
        self.btn_toggle_japanese.config(fg="green" if self.japanese_mode else "black")
        self.show_page()

    # ------------------ RESIZE ------------------
    def on_canvas_resize(self, event):
        if not self.original_imgs:
            return
        total_width = sum(img.width for img in self.original_imgs)
        max_height = max(img.height for img in self.original_imgs)
        self.base_zoom = compute_zoom(total_width, max_height, event.width, event.height)
        self.render_page()

    def update_page_label_position(self, event=None):
        footer_height = self.footer_frame.winfo_height() if hasattr(self, 'footer_frame') else 0
        padding = 5
        y_position = self.root.winfo_height() - footer_height - padding

        # move o bloco todo junto
        self.info_frame.place(x=10, y=y_position)