import tkinter as tk
from tkinter import ttk
from ui.dashboard.tab_reading import ReadingDashboard
from ui.dashboard.tab_ranking import ReadingRanking
from ui.dashboard.tab_ratings import RatingsDistribution

class DashboardMain(ttk.Frame):
    def __init__(self, parent, back_func=None):
        super().__init__(parent)
        self.back_func = back_func

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        notebook.add(ReadingDashboard(notebook), text="Dashboard de Leituras")
        notebook.add(ReadingRanking(notebook), text="Ranking de Leituras")
        notebook.add(RatingsDistribution(notebook), text="Distribuição de Avaliações")

        # botão de voltar
        if self.back_func:
            btn_frame = ttk.Frame(self)
            btn_frame.pack(fill="x")
            ttk.Button(btn_frame, text="Voltar", command=self.back_func).pack(pady=5)
