import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from db.queries import get_years, get_comic_readings, get_manga_readings
from utils.helpers import sort_tree


class ReadingRanking(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        # ------------------ Frame da esquerda ------------------
        self.tree_frame = tk.Frame(self)
        self.tree_frame.pack(side="left", fill="y", padx=5, pady=5)

        self.tree = ttk.Treeview(self.tree_frame, columns=("title", "series", "date"), show="headings")
        self.tree.pack(fill="y", expand=True)

        scrollbar = tk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.tree.heading("title", text="Título / Volume", command=lambda: sort_tree(self.tree, "title", False))
        self.tree.heading("series", text="Série", command=lambda: sort_tree(self.tree, "series", False))
        self.tree.heading("date", text="Data", command=lambda: sort_tree(self.tree, "date", False))

        self.tree.column("title", width=200)
        self.tree.column("series", width=150)
        self.tree.column("date", width=100)

        # ------------------ Frame da direita ------------------
        self.right_frame = tk.Frame(self)
        self.right_frame.pack(side="right", fill="both", expand=True)

        filter_frame = ttk.Frame(self.right_frame)
        filter_frame.pack(fill="x", pady=10)

        ttk.Label(filter_frame, text="Ano:").pack(side="left", padx=5)
        self.year_cb = ttk.Combobox(filter_frame, state="readonly")
        self.year_cb.pack(side="left", padx=5)
        years = get_years()
        self.year_cb["values"] = ["Todos"] + years
        self.year_cb.current(0)

        ttk.Label(filter_frame, text="Tipo:").pack(side="left", padx=5)
        self.type_cb = ttk.Combobox(filter_frame, state="readonly", values=["Todos","HQs","Mangás"])
        self.type_cb.pack(side="left", padx=5)
        self.type_cb.current(0)

        ttk.Button(filter_frame, text="Atualizar", command=self.plot_timeline).pack(side="left", padx=10)

        self.canvas_frame = ttk.Frame(self.right_frame)
        self.canvas_frame.pack(fill="both", expand=True)

        self.plot_timeline()

    # ------------------ Função principal ------------------
    def plot_timeline(self):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        year = self.year_cb.get()
        tipo = self.type_cb.get()

        results_hq = {}
        results_manga = {}
        item_details = {}

        if tipo in ("Todos","HQs"):
            for title, series_name, d in get_comic_readings(year):
                key = d[:4] if year=="Todos" else d[5:7]
                results_hq[key] = results_hq.get(key,0)+1
                item_details.setdefault(key, []).append((f"{title} (HQ)", series_name, d))

        if tipo in ("Todos","Mangás"):
            for volume, series_name, d in get_manga_readings(year):
                key = d[:4] if year=="Todos" else d[5:7]
                results_manga[key] = results_manga.get(key,0)+1
                item_details.setdefault(key, []).append((f"Volume {volume} (Mangá)", series_name, d))

        if not results_hq and not results_manga:
            ttk.Label(self.canvas_frame, text="Nenhum dado encontrado.").pack()
            return

        x = sorted(set(list(results_hq.keys()) + list(results_manga.keys()))) if year=="Todos" else [f"{i:02}" for i in range(1,13)]
        xlabel = "Ano" if year=="Todos" else "Mês"

        y_hq = [results_hq.get(k,0) for k in x]
        y_manga = [results_manga.get(k,0) for k in x]

        fig, ax = plt.subplots(figsize=(8,4))
        bars_hq = ax.bar(x, y_hq, color="royalblue", label="HQs")
        bars_manga = ax.bar(x, y_manga, bottom=y_hq, color="orange", label="Mangás")

        ax.set_xlabel(xlabel)
        ax.set_ylabel("Qtd de Leituras")
        ax.set_title(f"Leituras por {'ano' if year=='Todos' else 'mês'} ({tipo}, {year})")
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        def on_click(event):
            if event.inaxes == ax:
                for bar, key in zip(bars_hq, x):
                    if bar.contains(event)[0]:
                        self.show_items(item_details.get(key, []))
                        break
                for bar, key in zip(bars_manga, x):
                    if bar.contains(event)[0]:
                        self.show_items(item_details.get(key, []))
                        break

        fig.canvas.mpl_connect("button_press_event", on_click)

    def show_items(self, items):
        self.tree.delete(*self.tree.get_children())
        for title, series_name, d in items:
            self.tree.insert("", "end", values=(title, series_name, d))
