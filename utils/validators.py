from datetime import datetime, date
import os

def is_non_empty(value: str) -> bool:
    """Valida se o campo não está vazio."""
    return bool(value.strip())

def is_integer(value: str) -> bool:
    """Verifica se a string representa um número inteiro válido."""
    return value.isdigit()

def to_int_or_none(value: str):
    """Converte para int se for número, senão retorna None."""
    return int(value) if value.isdigit() else None

def is_valid_date(value: str, fmt: str = "%m/%d/%y") -> bool:
    """Verifica se a data é válida de acordo com o formato informado."""
    try:
        datetime.strptime(value, fmt)
        return True
    except ValueError:
        return False

def parse_date(value: str, fmt: str = "%m/%d/%y"):
    """Converte string em date, ou None se inválido."""
    try:
        return datetime.strptime(value, fmt).date()
    except ValueError:
        return None

def is_future_date(d: date) -> bool:
    """Verifica se a data está no futuro."""
    return d > date.today()

def validate_int(value: str) -> bool:
    """Retorna True se o valor for vazio ou um número inteiro."""
    return value == "" or value.isdigit()

def validate_issue(issue_str):
    """Verifica o número da edição."""
    try:
        return int(issue_str)
    except ValueError:
        return None

from datetime import datetime

def validate_reading_date(date_str):
    """Verifica a data de leitura."""
    if not date_str.strip():
        return None
    try:
        return datetime.strptime(date_str, "%m/%d/%y").date()
    except ValueError:
        return None

def validate_rating(rating):
    """Verifica a avaliação."""
    return rating if rating and rating > 0 else None

def is_image_file(filename):
    """Checa se o arquivo é uma imagem válida."""
    return filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif"))

def is_ctrl_pressed(event_state):
    """Checa se Ctrl está pressionado (para zoom)."""
    return (event_state & 0x0004) != 0

def is_valid_folder(path):
    """Verifica se o caminho é uma pasta válida"""
    return os.path.isdir(path)

def is_image_file(filename):
    """Verifica se o arquivo é uma imagem"""
    return filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif'))

#pra embelezar são essas#
#_______________________#

def validate_image_folder(path: str, extensions=(".jpg", ".jpeg", ".png")) -> list:
    if not os.path.exists(path) or not os.path.isdir(path):
        return []
    return [f for f in os.listdir(path) if f.lower().endswith(extensions)]

def validate_file_exists(path: str) -> bool:
    return os.path.exists(path) and os.path.isfile(path)

def validate_canvas_item(canvas, item_id) -> bool:
    return item_id in canvas.find_all()

def validate_comic_input(name: str, author: str, issue: str) -> bool:
    if not name.strip() or not author.strip() or not issue.strip():
        return False
    return True





def validate_year(year: str) -> bool:
    """Valida se o ano é 'Todos' ou um número de 4 dígitos"""
    return year == "Todos" or (year.isdigit() and len(year) == 4)

def validate_series_selection(value):
    """Valida string da seleção da série"""
    if not value or value.startswith("📊"):
        return None, None
    if value.startswith("HQ:"):
        return value.replace("HQ: ", ""), "comic"
    if value.startswith("Mangá:"):
        return value.replace("Mangá: ", ""), "manga"
    return None, None

