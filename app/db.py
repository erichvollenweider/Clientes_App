import os
import sys
import shutil
import platform
from pathlib import Path
import sqlite3

APP_NAME = "ClientesApp"  # cambiar si querés otro nombre
DB_FILENAME = "clientes.db"

def _user_data_dir():
    if platform.system() == "Windows":
        base = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA") or str(Path.home() / "AppData" / "Local")
    else:
        # Linux / macOS: usa XDG o home
        base = os.getenv("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    path = Path(base) / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path

# Ruta destino donde se guardará la DB (escribible por el usuario)
USER_DB_PATH = _user_data_dir() / DB_FILENAME

# Ruta de la DB incluida en el paquete (plantilla). Cuando uses PyInstaller, los recursos quedan en _MEIPASS.
BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
BUNDLED_DB = BASE_DIR / "database" / DB_FILENAME

# Si no existe la DB de usuario, copiar la plantilla embebida si existe
if not USER_DB_PATH.exists():
    try:
        if BUNDLED_DB.exists():
            shutil.copy2(BUNDLED_DB, USER_DB_PATH)
        else:
            # No hay plantilla: crear archivo vacío (init_db creará las tablas)
            USER_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            USER_DB_PATH.touch()
    except Exception:
        # si falla la copia, seguimos y permitimos que init_db cree la DB
        pass

#Para pruebas comentar: DB_PATH = str(USER_DB_PATH)
#Para desplegar la app comentar: B_PATH = "database/clientes.db" y descomentar la línea anterior
DB_PATH = str(USER_DB_PATH)
#DB_PATH = "database/clientes.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            apellido TEXT NOT NULL,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            telefono TEXT,
            fecha_llegada DATE,
            fecha_entrega DATE
        )
    """)
    conn.commit()
    conn.close()

def agregar_cliente(apellido, nombre, descripcion, telefono, fecha_llegada, fecha_entrega):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clientes (apellido, nombre, descripcion, telefono, fecha_llegada, fecha_entrega)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (apellido, nombre, descripcion, telefono, fecha_llegada, fecha_entrega))
    conn.commit()
    conn.close()

def obtener_clientes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes")
    rows = cursor.fetchall()
    conn.close()
    return rows

def eliminar_cliente(cliente_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
    conn.commit()
    conn.close()

def actualizar_cliente(cliente_id, apellido, nombre, descripcion, telefono, fecha_llegada, fecha_entrega):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE clientes
        SET apellido = ?, nombre = ?, descripcion = ?, telefono = ?, fecha_llegada = ?, fecha_entrega = ?
        WHERE id = ?
    """, (apellido, nombre, descripcion, telefono, fecha_llegada, fecha_entrega, cliente_id))
    conn.commit()
    conn.close()

def buscar_clientes(criterio):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = f"""
        SELECT * FROM clientes
        WHERE apellido LIKE ? OR nombre LIKE ? OR descripcion LIKE ? OR telefono LIKE ?
    """
    like_criterio = f"%{criterio}%"
    cursor.execute(query, (like_criterio, like_criterio, like_criterio, like_criterio))
    rows = cursor.fetchall()
    conn.close()
    return rows