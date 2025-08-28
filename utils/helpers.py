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
