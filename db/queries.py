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