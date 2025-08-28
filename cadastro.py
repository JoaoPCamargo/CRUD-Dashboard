import sqlite3
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from tkcalendar import DateEntry

DB_PATH = r"C:\CRUD-Dashboard\hqs.db"  # ajuste para o seu banco

class MainMenu:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Menu Principal")
        self.root.geometry("300x200")

        # Título principal
        tk.Label(self.root, text="Bem-vindo ao Chronica Verse", font=("Arial", 16, "bold")).pack(pady=(10, 2))

        # Subtítulo
        tk.Label(self.root, text="Seu Catálogo de Quadrinhos", font=("Arial", 12, "italic")).pack(pady=(0, 10))


        tk.Button(self.root, text="Adicionar Quadrinho", width=20, command=self.open_add).pack(pady=5)
        tk.Button(self.root, text="Consultar Quadrinhos", width=20, command=self.open_consult).pack(pady=5)

        dash_btn = tk.Button(self.root, text="📊", width=3, command=self.open_dashboard)
        dash_btn.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

        self.root.mainloop()

    def open_add(self):
        self.root.withdraw()  # esconde o menu
        add_window = tk.Toplevel()
        app = ComicAdd(add_window)  # chama o formulário principal
        app.set_back_func(lambda: self.back(add_window))

    def open_consult(self):
        self.root.withdraw()
        consult_window = tk.Toplevel()
        ComicConsult(consult_window, back_func=lambda: self.back(consult_window))

    def open_dashboard(self):
        popup = tk.Toplevel(self.root)
        popup.title("Dashboard")
        label = tk.Label(popup, text="Abrindo o dashboard...")
        label.pack(padx=20, pady=20)
        popup.update()
        os.startfile(r"C:\CRUD-Dashboard\DashHQs.pbix")
        popup.after(1000, popup.destroy)

    def back(self, win):
        win.destroy()
        self.root.deiconify()  # mostra o menu novamente

class ComicAdd:
    def __init__(self, root):
        self.root = root
        self.root.title("Cadastro de Quadrinhos")
        self.conn = sqlite3.connect(DB_PATH)

        # --- EDITORA ---
        tk.Label(root, text="Editora:").grid(row=0, column=0, sticky="w")
        self.publisher_cb = ttk.Combobox(root, state="readonly")
        self.publisher_cb.grid(row=0, column=1, padx=5, pady=5)
        self.publisher_cb.bind("<<ComboboxSelected>>", self.load_series)

        self.add_pub_btn = tk.Button(root, text="+", command=self.add_publisher)
        self.add_pub_btn.grid(row=0, column=2, padx=5)

        # --- SÉRIE ---
        tk.Label(root, text="Série:").grid(row=1, column=0, sticky="w")
        self.series_cb = ttk.Combobox(root, state="readonly")
        self.series_cb.grid(row=1, column=1, padx=5, pady=5)
        self.series_cb.bind("<<ComboboxSelected>>", self.load_arcs)

        self.add_series_btn = tk.Button(root, text="+", command=self.add_series)
        self.add_series_btn.grid(row=1, column=2, padx=5)

        # --- ARCO ---
        tk.Label(root, text="Arco:").grid(row=2, column=0, sticky="w")
        self.arc_cb = ttk.Combobox(root, state="readonly")
        self.arc_cb.grid(row=2, column=1, padx=5, pady=5)

        self.add_arc_btn = tk.Button(root, text="+", command=self.add_arc)
        self.add_arc_btn.grid(row=2, column=2, padx=5)

        # --- NÚMERO DA EDIÇÃO ---
        tk.Label(root, text="Número da Edição:").grid(row=3, column=0, sticky="w")
        self.issue_entry = tk.Entry(root)
        self.issue_entry.grid(row=3, column=1, padx=5, pady=5)

        # --- TÍTULO ---
        tk.Label(root, text="Título:").grid(row=4, column=0, sticky="w")
        self.title_entry = tk.Entry(root)
        self.title_entry.grid(row=4, column=1, padx=5, pady=5)

        # --- DATA DE LEITURA ---
        tk.Label(root, text="Data de Leitura:").grid(row=5, column=0, sticky="w")
        self.date_entry = DateEntry(root, width=12, background='purple', foreground='red', borderwidth=2)
        self.date_entry.grid(row=5, column=1, padx=5, pady=5)
        self.date_entry.delete(0, tk.END)  # limpa o campo para ficar “vazio”

        # --- AVALIAÇÃO ---
        tk.Label(root, text="Avaliação:").grid(row=6, column=0, sticky="w")
        self.avaliacao_var = tk.IntVar(value=0)

        stars_frame = tk.Frame(root)
        stars_frame.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        self.stars = []
        for i in range(1, 6):
            lbl = tk.Label(stars_frame, text="☆", font=("Arial", 18))
            lbl.grid(row=0, column=i, padx=2)
            lbl.bind("<Button-1>", lambda e, n=i: self.set_stars(n))
            self.stars.append(lbl)


        # --- BOTÃO SALVAR ---
        self.save_btn = tk.Button(root, text="Cadastrar Quadrinho", command=self.save_comic)
        self.save_btn.grid(row=7, column=0, padx=5, pady=10)

        # --- BOTÃO DASHBOARD ---
        self.dash_btn = tk.Button(root, text="📊", width=3, command=self.open_dashboard)
        self.dash_btn.grid(row=7, column=1, padx=5, pady=10, sticky="w")

        # --- BOTÃO VOLTAR AO MENU ---
        self.back_btn = tk.Button(root, text="Voltar ao Menu", command=self.back_to_menu)
        self.back_btn.grid(row=7, column=2, padx=5, pady=10)    

        self.load_publishers()

    def load_publishers(self):
        cur = self.conn.cursor()
        cur.execute("SELECT publisher_id, name FROM Publisher ORDER BY name")
        self.publishers = cur.fetchall()
        self.publisher_cb["values"] = [p[1] for p in self.publishers]

    def add_publisher(self):
        win = tk.Toplevel(self.root)
        win.title("Nova Editora")

        tk.Label(win, text="Nome da Editora:").pack(padx=10, pady=5)
        entry = tk.Entry(win)
        entry.pack(padx=10, pady=5)

        def salvar():
            nome = entry.get().strip()
            if not nome:
                messagebox.showerror("Erro", "Nome da editora não pode ser vazio!", parent=win)
                return
            cur = self.conn.cursor()
            try:
                cur.execute("INSERT INTO Publisher (name) VALUES (?)", (nome,))
                self.conn.commit()
                self.load_publishers()  # atualiza a lista
                messagebox.showinfo("Sucesso", "Editora adicionada!", parent=win)
                win.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", "Essa editora já existe!", parent=win)

        tk.Button(win, text="Salvar", command=salvar).pack(pady=10)

    def load_series(self, event=None):
        idx = self.publisher_cb.current()
        if idx < 0: 
            self.series_cb["values"] = []
            return

        publisher_id = self.publishers[idx][0]
        print(f"[DEBUG] Buscando séries para publisher_id={publisher_id}")

        cur = self.conn.cursor()
        cur.execute("SELECT series_id, name FROM Series WHERE publisher_id=? ORDER BY name", (publisher_id,))
        self.series = cur.fetchall()
        print(f"[DEBUG] Séries encontradas: {self.series}")

        if not self.series:
            messagebox.showinfo("Aviso", "Nenhuma série encontrada para esta editora.")
            self.series_cb["values"] = []
        else:
            self.series_cb["values"] = [s[1] for s in self.series]
        self.series_cb.set("")
        self.arc_cb.set("")
        self.arc_cb["values"] = []

    def add_series(self):
        idx = self.publisher_cb.current()
        if idx < 0:
            messagebox.showerror("Erro", "Selecione uma editora antes de criar a série!")
            return
        publisher_id = self.publishers[idx][0]

        win = tk.Toplevel(self.root)
        win.title("Nova Série")

        # Nome da série
        tk.Label(win, text="Nome da Série:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        entry_name = tk.Entry(win)
        entry_name.grid(row=0, column=1, padx=10, pady=5)

        # Ano de início
        tk.Label(win, text="Ano de Início:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        entry_start_year = tk.Entry(win)
        entry_start_year.grid(row=1, column=1, padx=10, pady=5)

        # Ano de fim
        tk.Label(win, text="Ano de Fim:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        entry_end_year = tk.Entry(win)
        entry_end_year.grid(row=2, column=1, padx=10, pady=5)

        # Total de edições
        tk.Label(win, text="Total de Edições:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        entry_total_issues = tk.Entry(win)
        entry_total_issues.grid(row=3, column=1, padx=10, pady=5)

        def salvar():
            nome = entry_name.get().strip()
            start_year_str = entry_start_year.get().strip()
            end_year_str = entry_end_year.get().strip()
            total_issues_str = entry_total_issues.get().strip()

            if not nome:
                messagebox.showerror("Erro", "Nome da série não pode ser vazio!", parent=win)
                return

            # Validações de inteiros ou NULL
            start_year = int(start_year_str) if start_year_str.isdigit() else None
            end_year = int(end_year_str) if end_year_str.isdigit() else None
            total_issues = int(total_issues_str) if total_issues_str.isdigit() else None

            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO Series (name, publisher_id, start_year, end_year, total_issues)
                VALUES (?, ?, ?, ?, ?)
            """, (nome, publisher_id, start_year, end_year, total_issues))
            self.conn.commit()

            self.load_series()
            messagebox.showinfo("Sucesso", "Série adicionada!", parent=win)
            win.destroy()

        tk.Button(win, text="Salvar", command=salvar).grid(row=4, column=0, columnspan=2, pady=10)

    def load_arcs(self, event=None):
        idx = self.series_cb.current()
        if idx < 0:
            self.arc_cb["values"] = []
            return

        series_id = self.series[idx][0]
        cur = self.conn.cursor()
        cur.execute("SELECT arc_id, name FROM Arc WHERE series_id=? ORDER BY name", (series_id,))
        self.arcs = cur.fetchall()

        self.arc_cb["values"] = [a[1] for a in self.arcs]
        self.arc_cb.set("")

    def add_arc(self):
        idx = self.series_cb.current()
        if idx < 0:
            messagebox.showerror("Erro", "Selecione uma série antes de criar o arco!")
            return
        series_id = self.series[idx][0]

        win = tk.Toplevel(self.root)
        win.title("Novo Arco")

        # Nome do arco
        tk.Label(win, text="Nome do Arco:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        entry_name = tk.Entry(win)
        entry_name.grid(row=0, column=1, padx=10, pady=5)

        # End issue (usuário digita ou deixa em branco)
        tk.Label(win, text="Última Edição (end_issue):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        entry_end = tk.Entry(win)
        entry_end.grid(row=1, column=1, padx=10, pady=5)

        def salvar():
            nome = entry_name.get().strip()
            end_issue_str = entry_end.get().strip()

            if not nome:
                messagebox.showerror("Erro", "Nome do arco não pode ser vazio!", parent=win)
                return

            if end_issue_str == "":
                end_issue = None  # salva NULL
            elif end_issue_str.isdigit():
                end_issue = int(end_issue_str)
            else:
                messagebox.showerror("Erro", "Última edição deve ser número ou ficar em branco!", parent=win)
                return

            start_issue = 1  # fixo

            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO Arc (name, series_id, start_issue, end_issue)
                VALUES (?, ?, ?, ?)
            """, (nome, series_id, start_issue, end_issue))
            self.conn.commit()

            self.load_arcs()
            messagebox.showinfo("Sucesso", "Arco adicionado!", parent=win)
            win.destroy()

        tk.Button(win, text="Salvar", command=salvar).grid(row=2, column=0, columnspan=2, pady=10)

    def save_comic(self):

        try:
            issue = int(self.issue_entry.get())
        except ValueError:
            messagebox.showerror("Erro", "Número da edição inválido!")
            return

        title = self.title_entry.get().strip()
        date_str = self.date_entry.get().strip()
        reading_date = None
        if date_str:
            try:
                reading_date = datetime.strptime(date_str, "%m/%d/%y").date()
                if reading_date > date.today():
                    messagebox.showerror("Erro", "A data de leitura não pode ser no futuro!")
                    return
            except ValueError:
                messagebox.showerror("Erro", "Data inválida!")
                return


        series_idx = self.series_cb.current()
        if series_idx < 0:
            messagebox.showerror("Erro", "Selecione uma série!")
            return
        series_id = self.series[series_idx][0]

        arc_idx = self.arc_cb.current()
        arc_id = self.arcs[arc_idx][0] if arc_idx >= 0 else None

        avaliacao = self.avaliacao_var.get()
        if avaliacao == 0:
            avaliacao = None

        cur = self.conn.cursor()
        cur.execute("INSERT INTO Comic (issue_number, title, reading_date, series_id, arc_id, rating) VALUES (?, ?, ?, ?, ?, ?)",
                    (issue, title if title else None, reading_date, series_id, arc_id, avaliacao))
        self.conn.commit()

        messagebox.showinfo("Sucesso", "Quadrinho cadastrado!")
        self.issue_entry.delete(0, tk.END)
        self.title_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.series_cb.set("")
        self.arc_cb.set("")

    def open_dashboard(self):
        # cria popup temporário
        popup = tk.Toplevel(self.root)
        popup.title("Dashboard")
        label = tk.Label(popup, text="Abrindo o dashboard...")
        label.pack(padx=20, pady=20)
        popup.update()
        # abre o arquivo do Power BI
        os.startfile(r"C:\CRUD-Dashboard\DashHQs.pbix")
        # fecha o popup após 1s
        popup.after(1000, popup.destroy)

    def set_stars(self, n):
        self.avaliacao_var.set(n)
        for i, lbl in enumerate(self.stars, start=1):
            if i <= n:
                lbl.config(text="★", fg="gold")
            else:
                lbl.config(text="☆", fg="gray")

    def set_back_func(self, func):
        self.back_func = func

    def back_to_menu(self):
        if hasattr(self, 'back_func'):
            self.back_func()

class ComicConsult:
    def __init__(self, master, back_func):
        self.master = master
        self.master.title("Consultar Quadrinhos")
        self.master.geometry("950x500")
        self.back_func = back_func

        # --- FRAME DOS BOTÕES SUPERIORES ---
        btn_frame = tk.Frame(master)
        btn_frame.pack(pady=5)

        self.back_btn = tk.Button(btn_frame, text="Voltar ao Menu", command=self.voltar)
        self.back_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.dash_btn = tk.Button(btn_frame, text="📊", width=3, command=self.open_dashboard)
        self.dash_btn.pack(side=tk.LEFT)

        # --- FRAME DOS FILTROS ---
        filtros_frame = ttk.LabelFrame(master, text="Filtros")
        filtros_frame.pack(fill="x", padx=10, pady=5)

        # Título
        tk.Label(filtros_frame, text="Título:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_titulo = tk.Entry(filtros_frame, width=25)
        self.entry_titulo.grid(row=0, column=1, padx=5, pady=5)

        # Edição
        tk.Label(filtros_frame, text="Edição:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        vcmd = master.register(self.validate_int)  # validação só de inteiros
        self.entry_edicao = tk.Entry(filtros_frame, width=10, validate="key", validatecommand=(vcmd, "%P"))
        self.entry_edicao.grid(row=0, column=3, padx=5, pady=5)


        # Série
        tk.Label(filtros_frame, text="Série:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.combo_serie = ttk.Combobox(filtros_frame, state="readonly", width=25)
        self.combo_serie.grid(row=1, column=1, padx=5, pady=5)

        # Arco
        tk.Label(filtros_frame, text="Arco:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.combo_arco = ttk.Combobox(filtros_frame, state="readonly", width=25)
        self.combo_arco.grid(row=1, column=3, padx=5, pady=5)

        # Editora
        tk.Label(filtros_frame, text="Editora:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.combo_editora = ttk.Combobox(filtros_frame, state="readonly", width=25)
        self.combo_editora.grid(row=2, column=1, padx=5, pady=5)

        # Botões de ação
        self.btn_pesquisar = ttk.Button(filtros_frame, text="Pesquisar", command=self.apply_filters)
        self.btn_pesquisar.grid(row=3, column=0, columnspan=2, pady=8)

        self.btn_limpar = ttk.Button(filtros_frame, text="Limpar Filtros", command=self.clear_filters)
        self.btn_limpar.grid(row=3, column=2, columnspan=2, pady=8)

        # --- TREEVIEW ---
        self.cols = ("ID", "Título", "Edição", "Data de Leitura", "Editora", "Série", "Arco", "Avaliação")
        self.tree = ttk.Treeview(master, columns=self.cols, show="headings")
        for col in self.cols:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c, False))
            self.tree.column(col, width=120)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.sort_orders = {col: False for col in self.cols}
        self.tree.bind("<Double-1>", self.on_double_click)
        self.load_filter_options()
        self.load_comics()

    def on_double_click(self, event):
        item = self.tree.selection()
        if not item:
            return
        values = self.tree.item(item, "values")
        comic_id = values[0]  # ID do quadrinho
        EditComicWindow(self.master, comic_id, refresh_func=self.load_comics)


    def validate_int(self, value):
        if value == "":
            return True
        return value.isdigit()
    
    def load_filter_options(self):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # séries
        cur.execute("SELECT DISTINCT name FROM Series ORDER BY name")
        series = ["Todas"] + [r[0] for r in cur.fetchall() if r[0]]
        self.combo_serie["values"] = series
        self.combo_serie.current(0)

        # arcos
        cur.execute("SELECT DISTINCT name FROM Arc ORDER BY name")
        arcos = ["Todos"] + [r[0] for r in cur.fetchall() if r[0]]
        self.combo_arco["values"] = arcos
        self.combo_arco.current(0)

        # editoras
        cur.execute("SELECT DISTINCT name FROM Publisher ORDER BY name")
        editoras = ["Todas"] + [r[0] for r in cur.fetchall() if r[0]]
        self.combo_editora["values"] = editoras
        self.combo_editora.current(0)

        conn.close()

    def apply_filters(self):
        conn = sqlite3.connect(DB_PATH)
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

        titulo = self.entry_titulo.get().strip()
        if titulo:
            query += " AND c.title LIKE ?"
            params.append(f"%{titulo}%")

        edicao = self.entry_edicao.get().strip()
        if edicao.isdigit():
            query += " AND c.issue_number = ?"
            params.append(int(edicao))

        serie = self.combo_serie.get()
        if serie and serie != "Todas":
            query += " AND s.name = ?"
            params.append(serie)

        arco = self.combo_arco.get()
        if arco and arco != "Todos":
            query += " AND a.name = ?"
            params.append(arco)

        editora = self.combo_editora.get()
        if editora and editora != "Todas":
            query += " AND p.name = ?"
            params.append(editora)

        query += " ORDER BY c.reading_date DESC"
        cur.execute(query, params)
        self.rows = cur.fetchall()
        conn.close()

        self.display_rows(self.rows)

    def clear_filters(self):
        """Reseta todos os filtros e recarrega os quadrinhos"""
        self.entry_titulo.delete(0, tk.END)
        self.entry_edicao.delete(0, tk.END)
        self.combo_serie.current(0)
        self.combo_arco.current(0)
        self.combo_editora.current(0)
        self.load_comics()

    def display_rows(self, rows):
        for i in self.tree.get_children():
            self.tree.delete(i)

        for row in rows:
            # rating -> converter para estrelas
            rating = row[7]
            if rating is None:
                stars = "—"
            else:
                stars = "★" * rating + "☆" * (5 - rating)

            display_row = row[:7] + (stars,)
            self.tree.insert("", tk.END, values=display_row)


    def load_comics(self):
        conn = sqlite3.connect(DB_PATH)
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
        self.rows = cur.fetchall()
        conn.close()
        self.display_rows(self.rows)

    def sort_column(self, col, reverse):
        col_index = self.cols.index(col)
        try:
            sorted_rows = sorted(self.rows, key=lambda x: (x[col_index] is None, x[col_index]), reverse=reverse)
        except TypeError:
            sorted_rows = sorted(self.rows, key=lambda x: str(x[col_index]), reverse=reverse)

        self.display_rows(sorted_rows)
        self.sort_orders[col] = not reverse
        self.tree.heading(col, command=lambda c=col: self.sort_column(c, self.sort_orders[col]))

    def voltar(self):
        self.master.destroy()
        if self.back_func:
            self.back_func()

    def open_dashboard(self):
        popup = tk.Toplevel(self.master)
        popup.title("Dashboard")
        label = tk.Label(popup, text="Abrindo o dashboard...")
        label.pack(padx=20, pady=20)
        popup.update()
        os.startfile(r"C:\CRUD-Dashboard\DashHQs.pbix")
        popup.after(1000, popup.destroy)

class EditComicWindow:
    def __init__(self, master, comic_id, refresh_func=None):
        self.master = tk.Toplevel(master)
        self.master.title("Editar Quadrinho")
        self.comic_id = comic_id
        self.refresh_func = refresh_func
        self.conn = sqlite3.connect(DB_PATH)

        cur = self.conn.cursor()
        cur.execute("""
            SELECT title, issue_number, reading_date, series_id, arc_id, rating
            FROM Comic
            WHERE comic_id = ?
        """, (comic_id,))
        row = cur.fetchone()
        if not row:
            messagebox.showerror("Erro", "Quadrinho não encontrado!")
            self.master.destroy()
            return

        self.title_val, self.issue_val, self.date_val, self.series_id_val, self.arc_id_val, self.rating_val = row

        # --- Título ---
        tk.Label(self.master, text="Título:").grid(row=0, column=0, sticky="w")
        self.title_entry = tk.Entry(self.master, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)
        self.title_entry.insert(0, self.title_val if self.title_val else "")

        # --- Edição ---
        tk.Label(self.master, text="Número da Edição:").grid(row=1, column=0, sticky="w")
        self.issue_entry = tk.Entry(self.master, width=10)
        self.issue_entry.grid(row=1, column=1, padx=5, pady=5)
        self.issue_entry.insert(0, str(self.issue_val))

        # --- Data de Leitura ---
        tk.Label(self.master, text="Data de Leitura (opcional):").grid(row=2, column=0, sticky="w")
        self.date_entry = DateEntry(self.master, width=12, background='purple', foreground='red', borderwidth=2, year=2025)
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)
        # Permitir em branco
        if self.date_val:
            try:
                dt = datetime.strptime(self.date_val, "%Y-%m-%d").date()
                self.date_entry.set_date(dt)
            except ValueError:
                self.date_entry.set_date(datetime.today().date())
        else:
            self.date_entry.set_date('')  # deixa vazio

        # --- Editora ---
        tk.Label(self.master, text="Editora:").grid(row=3, column=0, sticky="w")
        self.combo_editora = ttk.Combobox(self.master, state="readonly", width=25)
        self.combo_editora.grid(row=3, column=1, padx=5, pady=5)

        # --- Série ---
        tk.Label(self.master, text="Série:").grid(row=4, column=0, sticky="w")
        self.combo_serie = ttk.Combobox(self.master, state="readonly", width=25)
        self.combo_serie.grid(row=4, column=1, padx=5, pady=5)

        # --- Arco ---
        tk.Label(self.master, text="Arco:").grid(row=5, column=0, sticky="w")
        self.combo_arco = ttk.Combobox(self.master, state="readonly", width=25)
        self.combo_arco.grid(row=5, column=1, padx=5, pady=5)

        # --- Avaliação ---
        tk.Label(self.master, text="Avaliação:").grid(row=6, column=0, sticky="w")
        self.rating_var = tk.IntVar(value=self.rating_val if self.rating_val else 0)
        stars_frame = tk.Frame(self.master)
        stars_frame.grid(row=6, column=1, padx=5, pady=5, sticky="w")
        self.stars = []
        for i in range(1, 6):
            lbl = tk.Label(stars_frame, text="☆", font=("Arial", 18))
            lbl.grid(row=0, column=i, padx=2)
            lbl.bind("<Button-1>", lambda e, n=i: self.set_stars(n))
            self.stars.append(lbl)
        self.set_stars(self.rating_var.get())

        # --- Botão salvar ---
        tk.Button(self.master, text="Salvar Alterações", command=self.save_changes).grid(row=7, column=0, columnspan=2, pady=10)

        self.load_publishers_series_arcs()
        self.master.grab_set()

    def set_stars(self, n):
        self.rating_var.set(n)
        for i, lbl in enumerate(self.stars, start=1):
            if i <= n:
                lbl.config(text="★", fg="gold")
            else:
                lbl.config(text="☆", fg="gray")

    def load_publishers_series_arcs(self):
        cur = self.conn.cursor()

        # Editoras
        cur.execute("SELECT publisher_id, name FROM Publisher ORDER BY name")
        self.publishers = cur.fetchall()
        self.combo_editora["values"] = [p[1] for p in self.publishers]
        # Seleciona editora atual
        cur.execute("""
            SELECT p.publisher_id 
            FROM Comic c
            LEFT JOIN Series s ON c.series_id = s.series_id
            LEFT JOIN Publisher p ON s.publisher_id = p.publisher_id
            WHERE c.comic_id = ?
        """, (self.comic_id,))
        pub_id = cur.fetchone()[0]
        idx = next((i for i, p in enumerate(self.publishers) if p[0] == pub_id), 0)
        self.combo_editora.current(idx)

        # Séries (todas)
        cur.execute("SELECT series_id, name FROM Series ORDER BY name")
        self.series = cur.fetchall()
        self.combo_serie["values"] = [s[1] for s in self.series]
        # Seleciona série atual
        idx = next((i for i, s in enumerate(self.series) if s[0] == self.series_id_val), 0)
        self.combo_serie.current(idx)

        # Arcos (todas)
        cur.execute("SELECT arc_id, name FROM Arc ORDER BY name")
        self.arcs = cur.fetchall()
        self.combo_arco["values"] = [a[1] for a in self.arcs]
        # Seleciona arco atual
        if self.arc_id_val:
            idx = next((i for i, a in enumerate(self.arcs) if a[0] == self.arc_id_val), 0)
            self.combo_arco.current(idx)
        else:
            self.combo_arco.set('')  # nenhum arco

    def save_changes(self):
        title = self.title_entry.get().strip()
        try:
            issue = int(self.issue_entry.get())
        except ValueError:
            messagebox.showerror("Erro", "Número da edição inválido!")
            return

        # Data de leitura (opcional)
        date_str = self.date_entry.get()
        reading_date = None
        if date_str.strip():
            try:
                reading_date = datetime.strptime(date_str, "%m/%d/%y").date()
            except ValueError:
                messagebox.showerror("Erro", "Data de leitura inválida!")
                return

        # Série
        series_idx = self.combo_serie.current()
        series_id = self.series[series_idx][0] if series_idx >= 0 else None

        # Arco
        arc_idx = self.combo_arco.current()
        arc_id = self.arcs[arc_idx][0] if arc_idx >= 0 else None

        # Avaliação
        rating = self.rating_var.get() if self.rating_var.get() > 0 else None

        cur = self.conn.cursor()
        cur.execute("""
            UPDATE Comic
            SET title = ?, issue_number = ?, reading_date = ?, series_id = ?, arc_id = ?, rating = ?
            WHERE comic_id = ?
        """, (title if title else None, issue, reading_date, series_id, arc_id, rating, self.comic_id))
        self.conn.commit()
        messagebox.showinfo("Sucesso", "Quadrinho atualizado!")
        if self.refresh_func:
            self.refresh_func()
        self.master.destroy()

if __name__ == "__main__":
    MainMenu()
