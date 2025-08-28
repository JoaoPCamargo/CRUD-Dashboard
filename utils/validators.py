from datetime import datetime, date

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
