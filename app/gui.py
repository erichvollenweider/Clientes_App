import tkinter as tk
import datetime
from tkinter import messagebox
from tkcalendar import DateEntry
from app.db import agregar_cliente, obtener_clientes, eliminar_cliente, actualizar_cliente, buscar_clientes

def crear_gui():
    root = tk.Tk()
    root.title("Gestión de Clientes")
    root.geometry("1050x780")

    # --- Campos (una columna clara: etiqueta col=0, input col=1) ---
    tk.Label(root, text="Apellido:").grid(row=0, column=0, sticky="w", padx=10, pady=6)
    entry_apellido = tk.Entry(root, width=35)
    entry_apellido.grid(row=0, column=1, pady=6, sticky="w")

    tk.Label(root, text="Nombre:").grid(row=1, column=0, sticky="w", padx=10, pady=6)
    entry_nombre = tk.Entry(root, width=35)
    entry_nombre.grid(row=1, column=1, pady=6, sticky="w")

    tk.Label(root, text="Descripción:").grid(row=2, column=0, sticky="w", padx=10, pady=6)
    entry_descripcion = tk.Entry(root, width=35)
    entry_descripcion.grid(row=2, column=1, pady=6, sticky="w")

    tk.Label(root, text="Teléfono:").grid(row=3, column=0, sticky="w", padx=10, pady=6)
    entry_telefono = tk.Entry(root, width=35)
    entry_telefono.grid(row=3, column=1, pady=6, sticky="w")

    tk.Label(root, text="Fecha llegada:").grid(row=4, column=0, sticky="w", padx=10, pady=6)
    entry_inicio = DateEntry(root, date_pattern="dd-mm-yyyy")
    entry_inicio.grid(row=4, column=1, pady=6, sticky="w")

    tk.Label(root, text="Fecha entrega:").grid(row=5, column=0, sticky="w", padx=10, pady=6)
    entry_entrega = DateEntry(root, date_pattern="dd-mm-yyyy")
    entry_entrega.grid(row=5, column=1, pady=6, sticky="w")

    # --- Acciones ---
    def guardar_cliente():
        apellido= entry_apellido.get().strip()
        nombre = entry_nombre.get().strip()
        descripcion = entry_descripcion.get().strip()
        telefono = entry_telefono.get().strip()
        fecha_llegada = entry_inicio.get_date().strftime("%Y-%m-%d")
        fecha_entrega = entry_entrega.get_date().strftime("%Y-%m-%d")

        if not apellido:
            messagebox.showerror("Error", "El apellido es obligatorio.")
            return

        agregar_cliente(apellido, nombre, descripcion, telefono, fecha_llegada, fecha_entrega)
        messagebox.showinfo("Éxito", "Cliente agregado correctamente.")
        entry_apellido.delete(0, tk.END)
        entry_nombre.delete(0, tk.END)
        entry_descripcion.delete(0, tk.END)
        entry_telefono.delete(0, tk.END)
        actualizar_lista()

    def eliminar():
        seleccion = lista.curselection()
        if not seleccion:
            messagebox.showerror("Error", "Selecciona un cliente para eliminar.")
            return
        item_text = lista.get(seleccion[0])
        cliente_id = item_text.split(" - ")[0]
        if messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar este cliente?"):
            eliminar_cliente(cliente_id)
            actualizar_lista()
            messagebox.showinfo("Éxito", "Cliente eliminado correctamente.")

    def editar():
        seleccion = lista.curselection()
        if not seleccion:
            messagebox.showerror("Error", "Selecciona un cliente para editar.")
            return

        item_text = lista.get(seleccion[0])
        cliente_id = item_text.split(" - ")[0]

        # Ventana emergente
        win = tk.Toplevel(root)
        win.title("Editar cliente")
        win.geometry("400x300")

        # Labels y entries...
        tk.Label(win, text="Apellido:").grid(row=0, column=0, sticky="w", padx=10, pady=6)
        entry_ap = tk.Entry(win)
        entry_ap.grid(row=0, column=1, pady=6, sticky="w")

        tk.Label(win, text="Nombre:").grid(row=1, column=0, sticky="w", padx=10, pady=6)
        entry_nom = tk.Entry(win)
        entry_nom.grid(row=1, column=1, pady=6, sticky="w")

        tk.Label(win, text="Descripción:").grid(row=2, column=0, sticky="w", padx=10, pady=6)
        entry_desc = tk.Entry(win)
        entry_desc.grid(row=2, column=1, pady=6, sticky="w")

        tk.Label(win, text="Teléfono:").grid(row=3, column=0, sticky="w", padx=10, pady=6)
        entry_tel = tk.Entry(win)
        entry_tel.grid(row=3, column=1, pady=6, sticky="w")

        tk.Label(win, text="Fecha llegada:").grid(row=4, column=0, sticky="w", padx=10, pady=6)
        entry_fi = DateEntry(win, date_pattern="dd-mm-yyyy")
        entry_fi.grid(row=4, column=1, pady=6, sticky="w")

        tk.Label(win, text="Fecha entrega:").grid(row=5, column=0, sticky="w", padx=10, pady=6)
        entry_fe = DateEntry(win, date_pattern="dd-mm-yyyy")
        entry_fe.grid(row=5, column=1, pady=6, sticky="w")

        # Cargar datos actuales
        for c in obtener_clientes():
            if str(c[0]) == cliente_id:
                entry_ap.insert(0, c[1])
                entry_nom.insert(0, c[2])
                entry_desc.insert(0, c[3] if c[3] else "")
                entry_tel.insert(0, c[4] if c[4] else "")
                if c[5]:
                    try:
                        # c[5] suele venir como 'YYYY-MM-DD' desde la BD -> convertir a date
                        if isinstance(c[5], str):
                            entry_fi.set_date(datetime.date.fromisoformat(c[5]))
                        else:
                            entry_fi.set_date(c[5])
                    except Exception:
                        # fallback silencioso si el formato es inesperado
                        pass
                if c[6]:
                    try:
                        if isinstance(c[6], str):
                            entry_fe.set_date(datetime.date.fromisoformat(c[6]))
                        else:
                            entry_fe.set_date(c[6])
                    except Exception:
                        pass

        def guardar_cambios():
            try:
                actualizar_cliente(
                    int(cliente_id),
                    entry_ap.get().strip(),
                    entry_nom.get().strip(),
                    entry_desc.get().strip(),
                    entry_tel.get().strip(),
                    entry_fi.get_date().strftime("%Y-%m-%d"),
                    entry_fe.get_date().strftime("%Y-%m-%d"),
                )
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar: {e}")
                return
            messagebox.showinfo("Éxito", "Cliente actualizado.")
            win.destroy()
            actualizar_lista()

        tk.Button(win, text="Guardar Cambios", command=guardar_cambios).grid(row=7, column=1, pady=6, sticky="w")
        win.update_idletasks()
        win.minsize(win.winfo_reqwidth(), win.winfo_reqheight())
        win.transient(root); win.grab_set(); win.focus_set()
        


    tk.Label(root, text="Buscar:").grid(row=7, column=0, padx=10, sticky="w")
    entry_buscar = tk.Entry(root, width=35)
    entry_buscar.grid(row=7, column=1, sticky="w", pady=6)

    def buscar():
        criterio = entry_buscar.get().strip()
        lista.delete(0, tk.END)
        for c in buscar_clientes(criterio):
            cid, ap, nom, desc, tel, fi, fe = c
            fi = fmt_fecha(fi)
            fe = fmt_fecha(fe)
            lista.insert(tk.END, f"{cid} - {ap}, {nom} | {desc} | Tel: {tel} | ({fi} a {fe})")

    tk.Button(root, text="Buscar", command=buscar).grid(row=7, column=1, sticky="w", padx=300)

    # Botones
    tk.Button(root, text="Guardar", command=guardar_cliente).grid(row=6, column=1, pady=10, sticky="w")
    
    # Frame que contiene lista y botones
    frame_lista = tk.Frame(root)
    frame_lista.grid(row=8, column=0, columnspan=3, padx=10, pady=10, sticky="we")

    # Lista
    lista = tk.Listbox(frame_lista, width=80, height=12)
    lista.grid(row=0, column=0, rowspan=2, padx=5, pady=5, sticky="w")

    # Sub-frame para los botones (columna derecha)
    frame_botones = tk.Frame(frame_lista)
    frame_botones.grid(row=0, column=1, sticky="n", padx=10)

    # Botones a la derecha
    btn_editar = tk.Button(frame_botones, text="Editar", command=editar, width=10)
    btn_editar.pack(pady=(0, 2))  # arriba 0, abajo 2 píxeles

    btn_eliminar = tk.Button(frame_botones, text="Eliminar", command=eliminar, width=10)
    btn_eliminar.pack(pady=(2, 0))  # arriba 2, abajo 0

    

    def fmt_fecha(iso):
        if not iso:
            return "-"
        try:
            y, m, d = iso.split("-")
            return f"{d}-{m}-{y}"
        except Exception:
            return iso  # por si viniera en otro formato

    def actualizar_lista():
        lista.delete(0, tk.END)
        for c in obtener_clientes():
            # c: (id, apellido, nombre, descripcion, telefono, fecha_llegada, fecha_entrega)
            cid = c[0]
            apellido = c[1] if c[1] else "-"
            nombre = c[2] if c[2] else "-"
            desc = c[3] if c[3] else "-"
            tel = c[4] if c[4] else "-"
            fi = fmt_fecha(c[5])  # fecha_llegada
            fe = fmt_fecha(c[6])  # fecha_entrega
            lista.insert(
                tk.END,
                f"{cid} - {apellido}, {nombre} | {desc} | Tel: {tel} | ({fi} a {fe})"
            )

    actualizar_lista()
    root.mainloop()
