import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "db", "hqs.db")
DASHBOARD_PATH = os.path.join(BASE_DIR, "dashboards", "dashboard.pbix")
ICON_PATH = os.path.join(BASE_DIR, "assets", "app.ico")