import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from db.queries import get_all_series, get_ratings
from utils.helpers import calculate_distribution, calculate_average
from utils.validators import validate_series_selection


class RatingsDistribution(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.selected_series = None
        self.series_type = None

        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        # Lista de séries
        self.series_listbox = tk.Listbox(main_frame, width=25, exportselection=False)
        self.series_listbox.pack(side="left", fill="y", padx=5, pady=5)
        self.series_listbox.bind("<<ListboxSelect>>", self.on_series_select)

        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.series_listbox.yview)
        scrollbar.pack(side="left", fill="y")
        self.series_listbox.config(yscrollcommand=scrollbar.set)

        # Frame da direita
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="left", fill="both", expand=True)

        self.canvas_frame = ttk.Frame(right_frame)
        self.canvas_frame.pack(fill="both", expand=True)

        self.load_series()
        self.plot_distribution()

    def load_series(self):
        comics, mangas = get_all_series()
        self.series_listbox.delete(0, tk.END)
        self.series_listbox.insert(tk.END, "📊 Todas as séries")
        for s in comics:
            self.series_listbox.insert(tk.END, f"HQ: {s}")
        for s in mangas:
            self.series_listbox.insert(tk.END, f"Mangá: {s}")

    def on_series_select(self, event):
        idx = self.series_listbox.curselection()
        if not idx:
            self.selected_series, self.series_type = None, None
        else:
            value = self.series_listbox.get(idx[0])
            self.selected_series, self.series_type = validate_series_selection(value)
        self.plot_distribution()

    def plot_distribution(self):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        ratings_comics, ratings_mangas = get_ratings(self.selected_series, self.series_type)

        if not ratings_comics and not ratings_mangas:
            ttk.Label(self.canvas_frame, text="Nenhuma avaliação encontrada.").pack()
            return

        counts_comics, counts_mangas, totals = calculate_distribution(ratings_comics, ratings_mangas)
        if sum(totals) == 0:
            ttk.Label(self.canvas_frame, text="Nenhuma avaliação encontrada.").pack()
            return

        notas_labels = [f"Nota {i+1}" for i, t in enumerate(totals) if t > 0]
        totals_filtrados = [t for t in totals if t > 0]
        media = calculate_average(ratings_comics, ratings_mangas)

        fig, ax = plt.subplots(figsize=(6, 6))
        outer_colors = plt.cm.Blues_r(range(5))

        ax.pie(
            totals_filtrados,
            radius=1,
            labels=notas_labels,
            labeldistance=0.8,
            colors=outer_colors[:len(totals_filtrados)],
            wedgeprops=dict(width=0.3, edgecolor="white")
        )

        subdivisoes, sub_labels, sub_colors = [], [], []
        for i, (c, m) in enumerate(zip(counts_comics, counts_mangas)):
            if c > 0:
                subdivisoes.append(c)
                sub_labels.append(f"HQ ({c})")
                sub_colors.append("royalblue")
            if m > 0:
                subdivisoes.append(m)
                sub_labels.append(f"Mangá ({m})")
                sub_colors.append("darkorange")

        ax.pie(
            subdivisoes,
            radius=0.7,
            labels=sub_labels,
            labeldistance=0.6,
            colors=sub_colors,
            wedgeprops=dict(width=0.3, edgecolor="white")
        )

        ax.text(0, 0, f"{media:.2f}", ha="center", va="center",
                fontsize=16, weight="bold", color="black")

        title = "Distribuição de Avaliações"
        if self.selected_series:
            title += f"\n{self.selected_series}"
        ax.set(aspect="equal", title=title)

        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
