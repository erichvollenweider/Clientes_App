import tkinter as tk
from tkinter import filedialog, messagebox
from app.db import obtener_clientes
import pandas as pd

def descargar_excel(parent=None):
    """
    Abre un diálogo para guardar la tabla de clientes a un archivo .xlsx.
    Si se llama desde la GUI, pasar root como `parent` para que el diálogo sea modal.
    Retorna la ruta guardada o None si se canceló.
    """
    own_root = False
    if parent is None:
        parent = tk.Tk()
        parent.withdraw()
        own_root = True

    try:
        rows = obtener_clientes()
        if not rows:
            messagebox.showinfo("Exportar", "No hay datos para exportar.", parent=parent)
            return None

        df = pd.DataFrame(rows, columns=["id", "Apellido", "Nombre", "Descripción", "Teléfono", "Fecha llegada", "Fecha entrega"])
        path = filedialog.asksaveasfilename(parent=parent,
                                            defaultextension=".xlsx",
                                            filetypes=[("Excel files", "*.xlsx")],
                                            title="Guardar Excel como")
        if not path:
            return None

        # Exportar usando openpyxl (asegurate de tener openpyxl instalado)
        df.drop(columns=["id"]).to_excel(path, index=False, engine="openpyxl")
        messagebox.showinfo("Exportar", f"Exportado a Excel:\n{path}", parent=parent)
        return path

    except ImportError:
        messagebox.showerror("Error", "Falta instalar pandas o openpyxl.\nEjecuta: pip install pandas openpyxl", parent=parent)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo exportar: {e}", parent=parent)
    finally:
        if own_root:
            parent.destroy()