import os
import sys
import shutil

# ==============================
# BASE PATH (exe vs script)
# ==============================
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS  # quando rodar empacotado no .exe
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==============================
# PASTA PERSISTENTE DO USUÁRIO
# ==============================
USER_DIR = os.path.join(os.path.expanduser("~"), "ChronicaVerse")
USER_DB = os.path.join(USER_DIR, "hqs.db")
USER_BACKGROUNDS = os.path.join(USER_DIR, "assets", "backgrounds")


os.makedirs(USER_DIR, exist_ok=True)
os.makedirs(USER_BACKGROUNDS, exist_ok=True)

# ==============================
# DB (cópia inicial, se não existir)
# ==============================
DB_SOURCE = os.path.join(BASE_DIR, "db", "hqs.db")
if not os.path.exists(USER_DB):
    try:
        shutil.copy(DB_SOURCE, USER_DB)
    except Exception as e:
        print(f"[ERRO] Não foi possível copiar o banco: {e}")

DB_PATH = USER_DB

# ==============================
# BACKGROUNDS (cópia inicial)
# ==============================
BG_SOURCE = os.path.join(BASE_DIR, "assets", "backgrounds")
if os.path.exists(BG_SOURCE):
    for file in os.listdir(BG_SOURCE):
        src = os.path.join(BG_SOURCE, file)
        dst = os.path.join(USER_BACKGROUNDS, file)
        if not os.path.exists(dst):
            try:
                shutil.copy(src, dst)
            except Exception as e:
                print(f"[ERRO] Não foi possível copiar fundo {file}: {e}")

BACKGROUND_PATH = USER_BACKGROUNDS

# ==============================
# ÍCONES (somente leitura, direto do exe)
# ==============================
ICON_PATH = os.path.join(BASE_DIR, "assets", "app.ico")
FOLDER_CBR_PATH = os.path.join(BASE_DIR, "assets", "folder_cbr.ico")
FOLDER_EMPTY_PATH = os.path.join(BASE_DIR, "assets", "folder_empty.ico")
