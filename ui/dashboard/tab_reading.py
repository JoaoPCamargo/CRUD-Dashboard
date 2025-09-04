import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from db.connection import get_connection
import db.queries as q
from utils.helpers import parse_dates, filter_dates_by_year
from utils.validators import validate_year


class ReadingDashboard(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.conn = get_connection()

        # ----- Sidebar -----
        self.sidebar = tk.Frame(self, width=220, bg="lightgray")
        self.sidebar.pack(side="left", fill="y")

        tk.Label(self.sidebar, text="Séries", font=("Arial", 12, "bold")).pack(pady=5)

        self.series = self.get_series_with_progress()
        for serie_id, name, progress, stype in self.series:
            frame = tk.Frame(self.sidebar, bg="white", relief="raised", bd=1)
            frame.pack(fill="x", pady=2, padx=2)

            lbl = tk.Label(frame, text=name, anchor="w")
            lbl.pack(side="left", padx=5)

            bar = ttk.Progressbar(frame, value=progress, length=80)
            bar.pack(side="right", padx=5)

            lbl.bind("<Button-1>", lambda e, sid=serie_id, st=stype, nm=name: self.update_dashboard(sid, st, nm))

        # ----- Main Frame -----
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(side="right", expand=True, fill="both")

        # Info
        self.info_frame = tk.Frame(self.main_frame)
        self.info_frame.pack(fill="x", pady=5)
        self.avg_label = tk.Label(self.info_frame, text="Avaliação Média: - | Leituras: -")
        self.avg_label.pack()

        # Filter
        self.filter_frame = tk.Frame(self.main_frame)
        self.filter_frame.pack(fill="x", pady=5)
        tk.Label(self.filter_frame, text="Filtrar por ano:").pack(side="left", padx=5)

        self.year_var = tk.StringVar()
        self.year_combo = ttk.Combobox(self.filter_frame, textvariable=self.year_var, state="readonly")
        self.year_combo.pack(side="left")
        self.year_combo.bind("<<ComboboxSelected>>", self.filter_by_year)

        years = self.get_available_years()
        self.year_combo["values"] = ["Todos"] + years
        self.year_combo.current(0)

        # Chart
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.plot_timeline()

    def get_series_with_progress(self):
        cur = self.conn.cursor()
        results = []

        # HQ
        cur.execute(q.GET_SERIES_HQ)
        for sid, name, progress in cur.fetchall():
            results.append((sid, name, progress or 0, "comic"))

        # Mangá
        cur.execute(q.GET_SERIES_MANGA)
        for sid, name, progress in cur.fetchall():
            results.append((sid, name, progress or 0, "manga"))

        return results

    def get_available_years(self):
        cur = self.conn.cursor()
        cur.execute(q.GET_AVAILABLE_YEARS)
        return sorted([y for (y,) in cur.fetchall() if y])

    def plot_timeline(self, serie_id=None, stype=None, serie_name=None, year=None):
        self.ax.clear()
        cur = self.conn.cursor()

        # Todas as leituras
        cur.execute(q.GET_ALL_READING_DATES)
        all_dates = parse_dates(cur.fetchall())
        all_dates = filter_dates_by_year(all_dates, year)
        all_dates.sort()

        if all_dates:
            x = all_dates
            y = list(range(1, len(all_dates) + 1))
            self.ax.plot(x, y, label="Todas as Leituras")

        # Série específica
        if serie_id and stype:
            if stype == "comic":
                cur.execute(q.GET_SERIE_READING_DATES_COMIC, (serie_id,))
            else:
                cur.execute(q.GET_SERIE_READING_DATES_MANGA, (serie_id,))

            serie_dates = parse_dates(cur.fetchall())
            serie_dates = filter_dates_by_year(serie_dates, year)
            serie_dates.sort()

            if serie_dates:
                y2 = list(range(1, len(serie_dates) + 1))
                self.ax.scatter(serie_dates, y2, color="red", label=serie_name)

        self.ax.set_title(f"Linha do Tempo ({year})" if validate_year(str(year)) and year != "Todos" else "Linha do Tempo de Leituras")
        self.ax.set_xlabel("Data")
        self.ax.set_ylabel("Leituras acumuladas")
        self.ax.legend()
        self.fig.autofmt_xdate()
        self.canvas.draw()

    def update_dashboard(self, serie_id, stype, serie_name):
        cur = self.conn.cursor()

        if stype == "comic":
            cur.execute(q.GET_SERIE_AVG_COMIC, (serie_id,))
        else:
            cur.execute(q.GET_SERIE_AVG_MANGA, (serie_id,))

        avg, count = cur.fetchone()
        avg = round(avg, 2) if avg else "-"
        self.avg_label.config(text=f"Avaliação Média: {avg} | Leituras avaliadas: {count}")

        year = self.year_var.get()
        self.plot_timeline(serie_id, stype, serie_name, year)

    def filter_by_year(self, event):
        year = self.year_var.get()
        self.plot_timeline(year=year)
