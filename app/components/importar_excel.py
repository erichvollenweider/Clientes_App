import tkinter as tk
from tkinter import filedialog, messagebox
from app.db import agregar_cliente
import datetime

def _parse_date(val):
    if val is None:
        return None
    try:
        import pandas as pd
        if isinstance(val, (pd.Timestamp, datetime.date, datetime.datetime)):
            return val.strftime("%Y-%m-%d")
    except Exception:
        pass
    s = str(val).strip()
    if not s or s.lower() == 'nan':
        return None
    for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%Y/%m/%d", "%d.%m.%Y"):
        try:
            return datetime.datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except Exception:
            pass
    try:
        dt = datetime.date.fromisoformat(s)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        pass
    return None

def importar_excel(parent=None, refresh_callback=None):
    """
    Importa un archivo Excel/CSV a la BD.
    Si se pasa refresh_callback (callable), se ejecuta al terminar la importación
    para que la GUI pueda actualizar la tabla (p.e. actualizar_tabla).
    Retorna (importados, saltados) o None si se canceló.
    """
    own_root = False
    if parent is None:
        parent = tk.Tk()
        parent.withdraw()
        own_root = True

    try:
        import pandas as pd
    except Exception:
        messagebox.showerror("Error", "Falta instalar pandas (pip install pandas openpyxl)", parent=parent)
        if own_root:
            parent.destroy()
        return None

    path = filedialog.askopenfilename(parent=parent,
                                      filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files","*.*")],
                                      title="Seleccionar archivo a importar")
    if not path:
        if own_root:
            parent.destroy()
        return None

    try:
        if path.lower().endswith((".csv",)):
            df = pd.read_csv(path)
        else:
            df = pd.read_excel(path, engine="openpyxl")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}", parent=parent)
        if own_root:
            parent.destroy()
        return None

    cols = {c.strip().lower().replace(" ", ""): c for c in df.columns}
    mapping = {
        "apellido": None,
        "nombre": None,
        "descripción": None,
        "descripcion": None,
        "teléfono": None,
        "telefono": None,
        "fechallegada": None,
        "fechaentrega": None,
    }
    for key in list(mapping.keys()):
        if key in cols:
            mapping[key] = cols[key]

    desc_col = mapping.get("descripcion") or mapping.get("descripción")
    tel_col = mapping.get("telefono") or mapping.get("teléfono")
    fi_col = mapping.get("fechallegada")
    fe_col = mapping.get("fechaentrega")
    ap_col = mapping.get("apellido")
    nom_col = mapping.get("nombre")
    if not ap_col or not nom_col:
        msg = ("No se detectaron columnas 'Apellido' y 'Nombre' en el archivo.\n"
               f"Columnas detectadas: {', '.join(df.columns.astype(str))}\n\n"
               "Asegurate de que el archivo tenga encabezados: Apellido, Nombre, Descripción, Teléfono, Fecha llegada, Fecha entrega")
        messagebox.showerror("Error", msg, parent=parent)
        if own_root:
            parent.destroy()
        return None

    total = len(df)
    if total == 0:
        messagebox.showinfo("Importar", "El archivo no contiene filas.", parent=parent)
        if own_root:
            parent.destroy()
        return None

    if not messagebox.askyesno("Confirmar importación", f"Se importarán {total} filas. Continuar?", parent=parent):
        if own_root:
            parent.destroy()
        return None

    importados = 0
    saltados = 0
    for _, row in df.iterrows():
        try:
            ap = row.get(ap_col) if ap_col else None
            nom = row.get(nom_col) if nom_col else None
            desc = row.get(desc_col) if desc_col else None
            tel = row.get(tel_col) if tel_col else None
            fi = row.get(fi_col) if fi_col else None
            fe = row.get(fe_col) if fe_col else None

            apellido = "" if ap is None else str(ap).strip()
            nombre = "" if nom is None else str(nom).strip()
            descripcion = "" if desc is None else str(desc).strip()
            telefono = "" if tel is None else str(tel).strip()
            fecha_llegada = _parse_date(fi)
            fecha_entrega = _parse_date(fe)

            if not apellido:
                saltados += 1
                continue

            agregar_cliente(apellido, nombre, descripcion, telefono, fecha_llegada, fecha_entrega)
            importados += 1
        except Exception:
            saltados += 1
            continue

    messagebox.showinfo("Importar", f"Importadas: {importados}\nSaltadas: {saltados}", parent=parent)

    # llamar callback para que la GUI actualice la tabla automáticamente
    try:
        if callable(refresh_callback):
            refresh_callback()
    except Exception:
        pass

    if own_root:
        parent.destroy()
    return (importados, saltados)