-- 1. Editora
CREATE TABLE Publisher (
    publisher_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT NOT NULL UNIQUE
);

-- 2. Série
CREATE TABLE Series (
    series_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT NOT NULL,
    publisher_id   INTEGER NOT NULL,
    start_year     INTEGER,
    end_year       INTEGER,
    FOREIGN KEY (publisher_id) REFERENCES Publisher(publisher_id)
);

-- 3. Arco de História
CREATE TABLE Arc (
    arc_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT NOT NULL,
    series_id      INTEGER NOT NULL,
    start_issue    INTEGER,
    end_issue      INTEGER,
    FOREIGN KEY (series_id) REFERENCES Series(series_id)
);

-- 4. Edição (quadrinho individual)
CREATE TABLE Comic (
    comic_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_number   INTEGER NOT NULL,
    title          TEXT,
    release_date   DATE,
    series_id      INTEGER NOT NULL,
    arc_id         INTEGER,
    FOREIGN KEY (series_id) REFERENCES Series(series_id),
    FOREIGN KEY (arc_id) REFERENCES Arc(arc_id)
);

-- 5. Progresso de leitura
CREATE TABLE ReadingProgress (
    progress_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    comic_id       INTEGER NOT NULL,
    status         TEXT CHECK(status IN ('nao lido', 'em andamento', 'lido')) DEFAULT 'nao lido',
    date_started   DATE,
    date_finished  DATE,
    rating         INTEGER CHECK(rating BETWEEN 0 AND 10),
    FOREIGN KEY (comic_id) REFERENCES Comic(comic_id)
);
