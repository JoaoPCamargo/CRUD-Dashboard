import os
import random
from PIL import Image, ImageTk
import tkinter as tk
from datetime import datetime

def clear_entries(*entries):
    """Limpa vários campos de entrada Tkinter."""
    for entry in entries:
        entry.delete(0, "end")

def stars_display(n: int, max_stars: int = 5) -> list[str]:
    """Retorna lista de estrelas (★ e ☆) para exibição."""
    return ["★" if i < n else "☆" for i in range(max_stars)]

def stars_text(n: int, max_stars: int = 5) -> str:
    """Versão em string das estrelas, ex.: ★★★☆☆"""
    return "★" * n + "☆" * (max_stars - n)

def rating_to_stars(rating: int | None, max_stars: int = 5) -> str:
    """Converte uma nota (0–max_stars) em uma string de estrelas ★☆."""
    if rating is None:
        return "—"
    return "★" * rating + "☆" * (max_stars - rating)

def find_index_by_id(items, item_id):
    """items é lista de tuplas (id, nome). Retorna índice do item com id ou 0."""
    return next((i for i, it in enumerate(items) if it[0] == item_id), 0)

def clamp(value, min_value, max_value):
    """Garante que um valor esteja dentro do intervalo [min_value, max_value]."""
    return max(min_value, min(value, max_value))


def center_position(container_width, container_height, obj_width, obj_height):
    """Calcula coordenadas para centralizar objeto."""
    x = max((container_width - obj_width) // 2, 0)
    y = max((container_height - obj_height) // 2, 0)
    return x, y


def double_page_indices(current_page, total_pages, double_mode):
    """Retorna as páginas a exibir no modo duplo."""
    pages = [current_page]
    if double_mode and current_page < total_pages - 1:
        pages.append(current_page + 1)
    return pages


def compute_zoom(total_width, max_height, canvas_width, canvas_height):
    """Calcula o fator de zoom para caber a tela."""
    if canvas_width > 1 and canvas_height > 1:
        scale_w = canvas_width / total_width
        scale_h = canvas_height / max_height
        return min(scale_w, scale_h)
    return 1.0


def resize_images(img_list, zoom_factor):
    """Retorna uma lista de tuplas (width, height) de imagens redimensionadas."""
    resized_dims = []
    total_width = 0
    max_height = 0
    for img in img_list:
        w = int(img.width * zoom_factor)
        h = int(img.height * zoom_factor)
        resized_dims.append((w, h))
        total_width += w
        max_height = max(max_height, h)
    return resized_dims, total_width, max_height

def next_column(row, col, max_cols):
    """Calcula a próxima coluna e linha para exibição em grid"""
    col += 1
    if col >= max_cols:
        col = 0
        row += 1
    return row, col

def clear_history(history_list):
    """Limpa a história"""
    history_list.clear()
    return history_list



#--------------------------------#

# ---------------------------
# Imagem
# ---------------------------
def load_random_image_from_folder(folder: str, extensions=(".jpg", ".jpeg", ".png")) -> Image.Image:
    files = [f for f in os.listdir(folder) if f.lower().endswith(extensions)]
    if not files:
        raise FileNotFoundError(f"Nenhuma imagem encontrada em {folder}")
    file = random.choice(files)
    return Image.open(os.path.join(folder, file))

def resize_image_for_canvas(image: Image.Image, width: int, height: int) -> ImageTk.PhotoImage:
    resized = image.resize((width, height), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(resized)

# ---------------------------
# Canvas
# ---------------------------
def create_outlined_text(canvas, text, size, bold=False, italic=False, fill="#F5F5F5", outline="black"):
    font_style = ("CC Wild Worlds Roman", size, "bold" if bold else "normal")
    if italic:
        font_style += ("italic",)
    
    items = []
    offsets = [(-1,-1), (-1,1), (1,-1), (1,1)]
    for dx, dy in offsets:
        item = canvas.create_text(0, 0, text=text, font=font_style, fill=outline)
        items.append((item, dx, dy))
    
    main_item = canvas.create_text(0, 0, text=text, font=font_style, fill=fill)
    items.append((main_item, 0, 0))
    return items

def create_canvas_button(canvas, text, command, width=200, height=40, square=False):
    if square:
        width = height = max(width, height)
    btn = {}
    btn['width'] = width
    btn['height'] = height
    btn['rect'] = canvas.create_rectangle(0, 0, width, height, fill="#222222", outline="#555555", width=2)
    btn['text'] = canvas.create_text(0, 0, text=text, fill="white", font=("Arial", 12, "bold"))
    btn['command'] = command
    canvas.tag_bind(btn['rect'], "<Button-1>", lambda e, b=btn: b['command']())
    canvas.tag_bind(btn['text'], "<Button-1>", lambda e, b=btn: b['command']())
    return btn

def center_canvas_item(canvas, item_id, x, y, dx=0, dy=0):
    canvas.coords(item_id, x + dx, y + dy)






#######MANGAS####

def parse_volumes(volumes_text: str) -> list[int]:
    volumes = set()
    for part in volumes_text.split(','):
        part = part.strip()
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                if start > end:
                    raise ValueError(f"Intervalo inválido: {part}")
                volumes.update(range(start, end + 1))
            except Exception:
                raise ValueError(f"Intervalo inválido: {part}")
        else:
            try:
                volumes.add(int(part))
            except Exception:
                raise ValueError(f"Volume inválido: {part}")
    return sorted(volumes)



#######################################

from datetime import datetime

def parse_dates(rows):
    """Converte lista de tuplas [(date,), ...] em lista de datetime"""
    return [datetime.strptime(d, "%Y-%m-%d") for d, in rows if d]

def filter_dates_by_year(dates, year):
    if not year or year == "Todos":
        return dates
    return [d for d in dates if d.strftime("%Y") == year]


def sort_tree(tree, col, reverse):
    """Ordena Treeview por coluna, inclusive datas."""
    data = [(tree.set(k, col), k) for k in tree.get_children('')]
    if col == "date":
        data = [(datetime.strptime(v, "%Y-%m-%d"), k) for v, k in data]

    data.sort(reverse=reverse)
    for index, (val, k) in enumerate(data):
        tree.move(k, '', index)

    tree.heading(col, command=lambda: sort_tree(tree, col, not reverse))

def calculate_distribution(ratings_comics, ratings_mangas):
    """Conta as avaliações de HQs e Mangás (1 a 5)"""
    counts_comics = [ratings_comics.count(i) for i in range(1, 6)]
    counts_mangas = [ratings_mangas.count(i) for i in range(1, 6)]
    totals = [c + m for c, m in zip(counts_comics, counts_mangas)]
    return counts_comics, counts_mangas, totals


def calculate_average(ratings_comics, ratings_mangas):
    """Calcula média geral"""
    all_ratings = ratings_comics + ratings_mangas
    if not all_ratings:
        return 0
    return sum(all_ratings) / len(all_ratings)

