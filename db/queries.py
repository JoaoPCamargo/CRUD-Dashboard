from db.connection import get_connection

# --- PUBLISHERS ---
def get_publishers():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT publisher_id, name FROM Publisher ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return rows

def insert_publisher(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO Publisher (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

# --- SERIES ---
def get_series():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT series_id, name FROM Series ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_series_by_publisher(publisher_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT series_id, name FROM Series WHERE publisher_id=? ORDER BY name", (publisher_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def insert_series(name, publisher_id, start_year=None, end_year=None, total_issues=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Series (name, publisher_id, start_year, end_year, total_issues)
        VALUES (?, ?, ?, ?, ?)
    """, (name, publisher_id, start_year, end_year, total_issues))
    conn.commit()
    conn.close()

# --- ARCS ---
def get_arcs():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT arc_id, name FROM Arc ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_arcs_by_series(series_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT arc_id, name FROM Arc WHERE series_id=? ORDER BY name", (series_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def insert_arc(name, series_id, start_issue=1, end_issue=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO Arc (name, series_id, start_issue, end_issue) VALUES (?, ?, ?, ?)",
                (name, series_id, start_issue, end_issue))
    conn.commit()
    conn.close()

# --- COMICS ---
def insert_comic(issue_number, title, reading_date, series_id, arc_id=None, rating=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Comic (issue_number, title, reading_date, series_id, arc_id, rating)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (issue_number, title, reading_date, series_id, arc_id, rating))
    conn.commit()
    conn.close()

def get_all_comics():
    conn = get_connection()
    cur = conn.cursor()
    query = """
    SELECT c.comic_id, c.title, c.issue_number, c.reading_date,
           p.name as publisher, s.name as series, a.name as arc, c.rating
    FROM Comic c
    LEFT JOIN Series s ON c.series_id = s.series_id
    LEFT JOIN Publisher p ON s.publisher_id = p.publisher_id
    LEFT JOIN Arc a ON c.arc_id = a.arc_id
    ORDER BY c.reading_date DESC
    """
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return rows

def get_comics_by_filters(titulo="", edicao=None, serie=None, arco=None, editora=None):
    conn = get_connection()
    cur = conn.cursor()

    query = """
    SELECT c.comic_id, c.title, c.issue_number, c.reading_date,
           p.name as publisher, s.name as series, a.name as arc, c.rating
    FROM Comic c
    LEFT JOIN Series s ON c.series_id = s.series_id
    LEFT JOIN Publisher p ON s.publisher_id = p.publisher_id
    LEFT JOIN Arc a ON c.arc_id = a.arc_id
    WHERE 1=1
    """
    params = []

    if titulo:
        query += " AND c.title LIKE ?"
        params.append(f"%{titulo}%")
    if edicao is not None:
        query += " AND c.issue_number = ?"
        params.append(edicao)
    if serie and serie != "Todas":
        query += " AND s.name = ?"
        params.append(serie)
    if arco and arco != "Todos":
        query += " AND a.name = ?"
        params.append(arco)
    if editora and editora != "Todas":
        query += " AND p.name = ?"
        params.append(editora)

    query += " ORDER BY c.reading_date DESC"

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def get_comic_by_id(comic_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT title, issue_number, reading_date, series_id, arc_id, rating
        FROM Comic
        WHERE comic_id = ?
    """, (comic_id,))
    row = cur.fetchone()
    conn.close()
    return row

def get_comic_publisher(comic_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.publisher_id 
        FROM Comic c
        LEFT JOIN Series s ON c.series_id = s.series_id
        LEFT JOIN Publisher p ON s.publisher_id = p.publisher_id
        WHERE c.comic_id = ?
    """, (comic_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def update_comic(comic_id, title, issue_number, reading_date, series_id, arc_id, rating):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE Comic
        SET title = ?, issue_number = ?, reading_date = ?, series_id = ?, arc_id = ?, rating = ?
        WHERE comic_id = ?
    """, (title, issue_number, reading_date, series_id, arc_id, rating, comic_id))
    conn.commit()
    conn.close()

def delete_comic_by_id(comic_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Comic WHERE comic_id = ?", (comic_id,))
    conn.commit()
    conn.close()

# --- MANGÁS ---

def get_manga_series():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT manga_series_id, name, author, total_volumes
        FROM MangaSeries
        ORDER BY name
    """)
    result = cursor.fetchall()
    conn.close()
    return result

def insert_manga_series(name, author, total_volumes=None):
    """
    Insere uma nova série de mangá.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO MangaSeries (name, author, total_volumes)
        VALUES (?, ?, ?)
    """, (name, author, total_volumes))
    conn.commit()
    conn.close()

def insert_manga_volumes(series_id, volumes, reading_date=None, rating=None):
    """
    Insere múltiplos volumes de uma série.
    volumes: lista de inteiros
    reading_date: datetime.date ou string 'yyyy-mm-dd'
    rating: inteiro de 1 a 5 ou None
    """
    conn = get_connection()
    cursor = conn.cursor()

    for vol in volumes:
        cursor.execute("""
            INSERT INTO Manga (volume, reading_date, rating, manga_series_id)
            VALUES (?, ?, ?, ?)
        """, (vol, reading_date, rating, series_id))

    conn.commit()
    conn.close()

def get_mangas_by_filters(titulo="", volume=None, serie=None, autor=None):
    """
    Retorna mangás filtrados por título (série), volume e autor.
    """
    conn = get_connection()
    cur = conn.cursor()

    query = """
    SELECT m.manga_id, m.volume, m.reading_date,
           ms.name as series, ms.author, m.rating
    FROM Manga m
    LEFT JOIN MangaSeries ms ON m.manga_series_id = ms.manga_series_id
    WHERE 1=1
    """
    params = []

    if titulo:
        query += " AND ms.name LIKE ?"
        params.append(f"%{titulo}%")
    if volume is not None:
        query += " AND m.volume = ?"
        params.append(volume)
    if serie and serie != "Todas":
        query += " AND ms.name = ?"
        params.append(serie)
    if autor and autor != "Todos":
        query += " AND ms.author = ?"
        params.append(autor)

    query += " ORDER BY m.reading_date DESC"

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def get_manga_by_id(manga_id):
    conn = get_connection()
    cur = conn.cursor()
    query = """
    SELECT m.manga_id, m.volume, m.reading_date, m.rating, ms.name, ms.author
    FROM Manga m
    JOIN MangaSeries ms ON m.manga_series_id = ms.manga_series_id
    WHERE m.manga_id = ?
    """
    cur.execute(query, (manga_id,))
    row = cur.fetchone()
    conn.close()
    return row

def get_mangas_by_filters(titulo=None, volume=None, serie=None, author=None):
    conn = get_connection()
    cur = conn.cursor()

    query = """
    SELECT m.manga_id, m.volume, m.reading_date, ms.name, ms.author, m.rating
    FROM Manga m
    JOIN MangaSeries ms ON m.manga_series_id = ms.manga_series_id
    WHERE 1=1
    """
    params = []

    if titulo:
        query += " AND ms.name LIKE ?"
        params.append(f"%{titulo}%")
    if volume:
        query += " AND m.volume = ?"
        params.append(volume)
    if serie:
        query += " AND ms.name = ?"
        params.append(serie)
    if author:
        query += " AND ms.author = ?"
        params.append(author)

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def update_manga(manga_id, reading_date=None, rating=None):
    """
    Atualiza a data de leitura e a avaliação de um mangá pelo ID.
    reading_date deve ser uma string no formato 'YYYY-MM-DD' ou None.
    rating deve ser um inteiro entre 1 e 5 ou None.
    """
    conn = get_connection()
    cur = conn.cursor()

    query = """
        UPDATE Manga
        SET reading_date = ?, rating = ?
        WHERE manga_id = ?
    """
    cur.execute(query, (reading_date, rating, manga_id))
    conn.commit()
    conn.close()

def get_manga_series_by_id(manga_series_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT manga_series_id, name, author
            FROM MangaSeries
            WHERE manga_series_id = ?
        """, (manga_series_id,))
        row = cur.fetchone()
    finally:
        conn.close()
    return row


def delete_manga_by_id(manga_id):
    """
    Exclui um mangá pelo ID
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM Manga WHERE manga_id = ?", (manga_id,))
        conn.commit()
    finally:
        conn.close()




def get_filter_options():
    conn = get_connection()
    cur = conn.cursor()

    # séries
    cur.execute("SELECT DISTINCT name FROM Series ORDER BY name")
    series = ["Todas"] + [r[0] for r in cur.fetchall() if r[0]]

    # arcos
    cur.execute("SELECT DISTINCT name FROM Arc ORDER BY name")
    arcos = ["Todos"] + [r[0] for r in cur.fetchall() if r[0]]

    # editoras
    cur.execute("SELECT DISTINCT name FROM Publisher ORDER BY name")
    editoras = ["Todas"] + [r[0] for r in cur.fetchall() if r[0]]

    conn.close()
    return series, arcos, editoras

#------------------------------------------------------------------------------


def get_manga_authors():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT author FROM MangaSeries ORDER BY author")
    authors = [r[0] for r in cur.fetchall()]
    conn.close()
    return authors
##########################################################################################

# --- Séries ---
GET_SERIES_HQ = """
    SELECT s.series_id, s.name,
           CAST(SUM(CASE WHEN c.reading_date IS NOT NULL THEN 1 ELSE 0 END) AS FLOAT) /
           CASE WHEN COUNT(c.comic_id)=0 THEN 1 ELSE COUNT(c.comic_id) END * 100 AS progress
    FROM Series s
    LEFT JOIN Comic c ON s.series_id = c.series_id
    GROUP BY s.series_id
"""

GET_SERIES_MANGA = """
    SELECT ms.manga_series_id, ms.name,
           CAST(SUM(CASE WHEN m.reading_date IS NOT NULL THEN 1 ELSE 0 END) AS FLOAT) /
           CASE WHEN COUNT(m.manga_id)=0 THEN 1 ELSE COUNT(m.manga_id) END * 100 AS progress
    FROM MangaSeries ms
    LEFT JOIN Manga m ON ms.manga_series_id = m.manga_series_id
    GROUP BY ms.manga_series_id
"""

# --- Anos disponíveis ---
GET_AVAILABLE_YEARS = """
    SELECT DISTINCT strftime('%Y', reading_date) FROM Comic WHERE reading_date IS NOT NULL
    UNION
    SELECT DISTINCT strftime('%Y', reading_date) FROM Manga WHERE reading_date IS NOT NULL
"""

# --- Linha do tempo ---
GET_ALL_READING_DATES = """
    SELECT reading_date FROM Comic WHERE reading_date IS NOT NULL
    UNION ALL
    SELECT reading_date FROM Manga WHERE reading_date IS NOT NULL
"""

GET_SERIE_READING_DATES_COMIC = """
    SELECT reading_date FROM Comic WHERE series_id=? AND reading_date IS NOT NULL
"""

GET_SERIE_READING_DATES_MANGA = """
    SELECT reading_date FROM Manga WHERE manga_series_id=? AND reading_date IS NOT NULL
"""

# --- Avaliações ---
GET_SERIE_AVG_COMIC = """
    SELECT AVG(rating), COUNT(*) FROM Comic
    WHERE series_id=? AND rating IS NOT NULL
"""

GET_SERIE_AVG_MANGA = """
    SELECT AVG(rating), COUNT(*) FROM Manga
    WHERE manga_series_id=? AND rating IS NOT NULL
"""


def get_years():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT strftime('%Y', reading_date) FROM Comic WHERE reading_date IS NOT NULL")
    comic_years = [row[0] for row in cur.fetchall() if row[0]]

    cur.execute("SELECT DISTINCT strftime('%Y', reading_date) FROM Manga WHERE reading_date IS NOT NULL")
    manga_years = [row[0] for row in cur.fetchall() if row[0]]

    conn.close()
    return sorted(set(comic_years + manga_years))


def get_comic_readings(year=None):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT c.title, s.name, c.reading_date
        FROM Comic c
        JOIN Series s ON c.series_id = s.series_id
        WHERE c.reading_date IS NOT NULL
    """
    params = []
    if year and year != "Todos":
        query += " AND strftime('%Y', c.reading_date) = ?"
        params.append(year)

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows


def get_manga_readings(year=None):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT m.volume, ms.name, m.reading_date
        FROM Manga m
        JOIN MangaSeries ms ON m.manga_series_id = ms.manga_series_id
        WHERE m.reading_date IS NOT NULL
    """
    params = []
    if year and year != "Todos":
        query += " AND strftime('%Y', m.reading_date) = ?"
        params.append(year)

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows

from .connection import get_connection

def get_all_series():
    """Retorna lista de todas as séries de HQ e Mangá"""
    conn = get_connection()
    cur = conn.cursor()

    # HQ
    cur.execute("""
        SELECT DISTINCT s.name
        FROM Comic c
        JOIN Series s ON c.series_id = s.series_id
        WHERE s.name IS NOT NULL
        ORDER BY s.name
    """)
    comics = [row[0] for row in cur.fetchall()]

    # Mangás
    cur.execute("""
        SELECT DISTINCT ms.name
        FROM Manga m
        JOIN MangaSeries ms ON m.manga_series_id = ms.manga_series_id
        WHERE ms.name IS NOT NULL
        ORDER BY ms.name
    """)
    mangas = [row[0] for row in cur.fetchall()]

    conn.close()
    return comics, mangas


def get_ratings(series_name=None, series_type=None):
    """
    Retorna ratings de acordo com a série.
    - series_type: "comic", "manga" ou None (geral)
    """
    conn = get_connection()
    cur = conn.cursor()

    if series_name and series_type == "comic":
        cur.execute("""
            SELECT c.rating
            FROM Comic c
            JOIN Series s ON c.series_id = s.series_id
            WHERE c.rating IS NOT NULL
            AND s.name = ?
        """, [series_name])
        ratings = [r for (r,) in cur.fetchall()]
        conn.close()
        return ratings, []
    
    elif series_name and series_type == "manga":
        cur.execute("""
            SELECT m.rating
            FROM Manga m
            JOIN MangaSeries ms ON m.manga_series_id = ms.manga_series_id
            WHERE m.rating IS NOT NULL
            AND ms.name = ?
        """, [series_name])
        ratings = [r for (r,) in cur.fetchall()]
        conn.close()
        return [], ratings

    else:
        cur.execute("SELECT rating FROM Comic WHERE rating IS NOT NULL")
        ratings_comics = [r for (r,) in cur.fetchall()]

        cur.execute("SELECT rating FROM Manga WHERE rating IS NOT NULL")
        ratings_mangas = [r for (r,) in cur.fetchall()]

        conn.close()
        return ratings_comics, ratings_mangas
