import tkinter as tk
import datetime
import re
from tkinter import messagebox, ttk, filedialog
from tkcalendar import DateEntry
from app.db import (
    agregar_cliente, obtener_clientes, eliminar_cliente,
    actualizar_cliente, buscar_clientes
)

from app.components.exportar_excel import exportar_excel
from app.components.importar_excel import importar_excel

def crear_gui():

    root = tk.Tk()
    root.title("Gestión de Clientes")
    root.geometry("1100x720")

    # ------------- Estilo para tabla con separadores (tema 'clam') -------------

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass
    style.configure("Treeview", rowheight=24)
    style.configure("Treeview.Heading", font=("", 10, "bold"))

    # Expandir la fila de la tabla
    root.grid_rowconfigure(8, weight=0)
    # Hacer que las primeras 2 columnas crezcan con la ventana
    root.grid_columnconfigure(0, weight=0)
    root.grid_columnconfigure(1, weight=0)

    # ------------- Formulario -------------

    tk.Label(root, text="Apellido:").grid(row=0, column=0, sticky="e", padx=10, pady=6)
    entry_apellido = tk.Entry(root, width=35)
    entry_apellido.grid(row=0, column=1, pady=6, sticky="w")

    tk.Label(root, text="Nombre:").grid(row=1, column=0, sticky="e", padx=10, pady=6)
    entry_nombre = tk.Entry(root, width=35)
    entry_nombre.grid(row=1, column=1, pady=6, sticky="w")

    tk.Label(root, text="Descripción:").grid(row=2, column=0, sticky="e", padx=10, pady=6)
    entry_descripcion = tk.Entry(root, width=35)
    entry_descripcion.grid(row=2, column=1, pady=6, sticky="w")

    tk.Label(root, text="Teléfono:").grid(row=3, column=0, sticky="e", padx=10, pady=6)
    entry_telefono = tk.Entry(root, width=35)
    entry_telefono.grid(row=3, column=1, pady=6, sticky="w")

    tk.Label(root, text="Fecha llegada:").grid(row=4, column=0, sticky="e", padx=10, pady=6)
    entry_inicio = DateEntry(root, date_pattern="dd-mm-yyyy")
    entry_inicio.grid(row=4, column=1, pady=6, sticky="w")

    tk.Label(root, text="Fecha entrega:").grid(row=5, column=0, sticky="e", padx=10, pady=6)
    entry_entrega = DateEntry(root, date_pattern="dd-mm-yyyy")
    entry_entrega.grid(row=5, column=1, pady=6, sticky="w")


    # ------------- Acciones de formulario -------------

    def guardar_cliente():
        apellido = entry_apellido.get().strip()
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
        actualizar_tabla()

    tk.Button(root, text="Guardar", command=guardar_cliente).grid(row=6, column=1, pady=10, sticky="w")

    # ------------- Buscar -------------

    tk.Label(root, text="Buscar:").grid(row=7, column=0, padx=10, sticky="e",pady=10)
    entry_buscar = tk.Entry(root, width=35)
    entry_buscar.grid(row=7, column=1, sticky="we", pady=10)

    # ------------- Botón Buscar (alineado a la derecha de la fila de búsqueda) -------------
    def buscar():
        criterio = entry_buscar.get().strip()
        if criterio:
            poblar_tabla(buscar_clientes(criterio))
        else:
            actualizar_tabla()
    tk.Button(root, text="Buscar", command=buscar).grid(row=7, column=2, padx=10, sticky="w",pady=10)

    # ------------- TABLA (Treeview) -------------

    columns = ("apellido", "nombre", "descripcion", "telefono", "fi", "fe")
    TREE_VISIBLE_ROWS = 12
    tree = ttk.Treeview(root, columns=columns, show="headings", selectmode="browse", height=TREE_VISIBLE_ROWS)
    tree.heading("apellido", text="Apellido")
    tree.heading("nombre", text="Nombre")
    tree.heading("descripcion", text="Descripción")
    tree.heading("telefono", text="Teléfono")
    tree.heading("fi", text="Fecha llegada")
    tree.heading("fe", text="Fecha entrega")

    # ------------- Anchuras y alineaciones -------------

    tree.column("apellido", width=160, minwidth=160, stretch=False, anchor="w")
    tree.column("nombre",   width=140, minwidth=140, stretch=False, anchor="w")
    tree.column("descripcion", width=240, minwidth=240, stretch=False, anchor="w")
    tree.column("telefono", width=120, minwidth=120, stretch=False, anchor="w")
    tree.column("fi",       width=120, minwidth=120, stretch=False, anchor="center")
    tree.column("fe",       width=120, minwidth=120, stretch=False, anchor="center")

    tree.grid(row=8, column=0, columnspan=5, sticky="nsew", padx=10, pady=10)

    # ------------- Scroll vertical de la tabla -------------

    # scroll_y = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    # tree.configure(yscrollcommand=scroll_y.set)
    # scroll_y.grid(row=8, column=2, sticky="ns", pady=10)


    # ------------- Botones de acción a la derecha de la tabla -------------
    
    action = tk.Frame(root)
    action.grid(row=8, column=6, sticky="n", padx=10, pady=10)
    tk.Button(action, text="Editar", command=lambda: editar()).pack(pady=(0, 6), fill="x")
    tk.Button(action, text="Eliminar", command=lambda: eliminar()).pack(pady=(0, 6), fill="x")
    tk.Button(action, text="Exportar Excel", command=lambda: exportar_excel(root)).pack(pady=(0, 6), fill="x")
    tk.Button(action, text="Importar Excel", command=lambda: importar_excel(root, refresh_callback=actualizar_tabla)).pack(pady=(0, 6), fill="x")

    # ------------- Utilidades -------------

    def fmt_fecha(iso):
        if not iso:
            return "-"
        try:
            y, m, d = str(iso).split("-")
            return f"{d}-{m}-{y}"
        except Exception:
            return str(iso)

    def limpiar_tabla():
        for item in tree.get_children():
            tree.delete(item)

    def poblar_tabla(rows):
        limpiar_tabla()
        for c in rows:
            cid, ap, nom, desc, tel, fi, fe = c  # (id, apellido, nombre, descripcion, telefono, fecha_llegada, fecha_entrega)
            tree.insert(
                "", "end",
                iid=str(cid),                  # guardamos el ID aquí, NO se muestra
                values=(ap or "-", nom or "-", desc or "-", tel or "-", fmt_fecha(fi), fmt_fecha(fe))
            )

    def actualizar_tabla():
        poblar_tabla(obtener_clientes())


    # ------------- Acciones Editar/Eliminar -------------

    def eliminar():
        sel = tree.selection()
        if not sel:
            messagebox.showerror("Error", "Selecciona un cliente para eliminar.")
            return
        cliente_id = int(sel[0])  # el iid es el ID
        if messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar este cliente?"):
            eliminar_cliente(cliente_id)
            actualizar_tabla()
            messagebox.showinfo("Éxito", "Cliente eliminado correctamente.")

    def editar():
        sel = tree.selection()
        if not sel:
            messagebox.showerror("Error", "Selecciona un cliente para editar.")
            return
        cliente_id = int(sel[0])

        # Ventana emergente
        win = tk.Toplevel(root)
        win.title("Editar cliente")
        win.geometry("420x320")
        win.transient(root); win.grab_set()

        # Campos
        tk.Label(win, text="Apellido:").grid(row=0, column=0, sticky="w", padx=10, pady=6)
        entry_ap = tk.Entry(win, width=30); entry_ap.grid(row=0, column=1, pady=6, sticky="w")

        tk.Label(win, text="Nombre:").grid(row=1, column=0, sticky="w", padx=10, pady=6)
        entry_nom = tk.Entry(win, width=30); entry_nom.grid(row=1, column=1, pady=6, sticky="w")

        tk.Label(win, text="Descripción:").grid(row=2, column=0, sticky="w", padx=10, pady=6)
        entry_desc = tk.Entry(win, width=30); entry_desc.grid(row=2, column=1, pady=6, sticky="w")

        tk.Label(win, text="Teléfono:").grid(row=3, column=0, sticky="w", padx=10, pady=6)
        entry_tel = tk.Entry(win, width=30); entry_tel.grid(row=3, column=1, pady=6, sticky="w")

        tk.Label(win, text="Fecha llegada:").grid(row=4, column=0, sticky="w", padx=10, pady=6)
        entry_fi = DateEntry(win, date_pattern="dd-mm-yyyy"); entry_fi.grid(row=4, column=1, pady=6, sticky="w")

        tk.Label(win, text="Fecha entrega:").grid(row=5, column=0, sticky="w", padx=10, pady=6)
        entry_fe = DateEntry(win, date_pattern="dd-mm-yyyy"); entry_fe.grid(row=5, column=1, pady=6, sticky="w")

        # Cargar datos desde la BD
        for c in obtener_clientes():
            if c[0] == cliente_id:
                entry_ap.insert(0, c[1] or "")
                entry_nom.insert(0, c[2] or "")
                entry_desc.insert(0, c[3] or "")
                entry_tel.insert(0, c[4] or "")
                if c[5]:
                    try:
                        entry_fi.set_date(datetime.date.fromisoformat(c[5]) if isinstance(c[5], str) else c[5])
                    except Exception: pass
                if c[6]:
                    try:
                        entry_fe.set_date(datetime.date.fromisoformat(c[6]) if isinstance(c[6], str) else c[6])
                    except Exception: pass
                break

        def guardar_cambios():
            try:
                actualizar_cliente(
                    cliente_id,
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
            actualizar_tabla()

        tk.Button(win, text="Guardar cambios", command=guardar_cambios).grid(row=6, column=0, columnspan=2, pady=10)


    # ------------- Cargar datos iniciales -------------

    actualizar_tabla()
    root.mainloop()

    ##Zebra striping (filas alternadas en color gris claro/blanco).

    ##Ancho dinámico: que las columnas se ajusten cuando cambias el tamaño de la ventana.

    ##Botones más modernos y colores con ttkbootstrap (1 línea de instalación: pip install ttkbootstrap).

    ##Ordenar columnas al hacer click en el encabezado (orden asc/desc).

    ##Exportar a Excel o CSV (muy fácil con pandas).
