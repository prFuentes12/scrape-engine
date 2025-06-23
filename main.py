import tkinter as tk
from tkinter import ttk, messagebox
from concurrent.futures import ThreadPoolExecutor, as_completed
from scraper.brokerdental import buscar_producto
from scraper.dentaliberica import buscar_dentaliberica
from scraper.proclinic import buscar_proclinic
from scraper.dentaltix import buscar_dentaltix
from scraper.dentalexpress import buscar_dentalexpress
from scraper.ciendental import buscar_100dental
import webbrowser

PROVEEDORES = {
    "Broker Dental": buscar_producto,
    "Dental Ibérica": buscar_dentaliberica,
    "Proclinic": buscar_proclinic,
    "Dentaltix": buscar_dentaltix,
    "Dental Express": buscar_dentalexpress,
    "100Dental": buscar_100dental
}

def convertir_precio(precio_str):
    try:
        if not precio_str or precio_str == "-":
            return float('inf')
        parte = precio_str.split("–")[0].replace("€", "").replace(",", ".").strip()
        return float(parte)
    except:
        return float('inf')

def abrir_enlace(event, tree, data):
    region = tree.identify_region(event.x, event.y)
    column = tree.identify_column(event.x)
    if region == "cell" and column == "#6":  # 6ª columna = Enlace
        selected = tree.identify_row(event.y)
        if selected:
            url = data.get(selected)
            if url and url != "-":
                webbrowser.open_new_tab(url)

def on_mouse_motion(event, tree):
    region = tree.identify_region(event.x, event.y)
    column = tree.identify_column(event.x)
    if region == "cell" and column == "#6":
        tree.config(cursor="hand2")
    else:
        tree.config(cursor="")

def actualizar_filtro(tree, data_map, all_data, status, proveedor):
    for row in tree.get_children():
        tree.delete(row)

    filtrados = [item for item in all_data if proveedor == "Todos" or item["Proveedor"] == proveedor]
    if filtrados:
        for item in filtrados:
            row_id = tree.insert('', 'end', values=(
                item["Proveedor"], item["Nombre"], item["Precio Descuento"],
                item["Precio Original"], item["Descuento"], "Ir al producto"
            ), tags=("link",))
            data_map[row_id] = item["Enlace"]
        status.set(f"✅ {len(filtrados)} productos encontrados.")
    else:
        status.set("⚠️ No se encontraron resultados con ese filtro.")

def ejecutar_busqueda(termino, tree, status, data_map, all_data, proveedor_box):
    if not termino.strip():
        messagebox.showwarning("Campo vacío", "Por favor ingresa un término de búsqueda.")
        return

    for row in tree.get_children():
        tree.delete(row)
    status.set(f"🔍 Buscando '{termino}' en todos los proveedores...")

    data_map.clear()
    all_data.clear()

    def ejecutar_scraper(nombre, funcion):
        try:
            productos = funcion(termino)
            resultado = []
            for prod in productos:
                resultado.append({
                    "Proveedor": nombre,
                    "Nombre": " - ".join(part.strip() for part in prod.get("nombre", "").split("–") if part.strip()) or "N/D",
                    "Precio Descuento": prod.get("precio") or "-",
                    "Precio Original": prod.get("precio_original") or "-",
                    "Descuento": "-" if (prod.get("descuento") or "").lower().startswith("sin") else prod.get("descuento") or "-",
                    "Enlace": prod.get("url") or "-",
                    "PrecioNum": convertir_precio(prod.get("precio") or prod.get("precio_original") or "")
                })
            return (nombre, resultado)
        except Exception as e:
            return (nombre, f"❌ Error con {nombre}: {e}")

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(ejecutar_scraper, nombre, func) for nombre, func in PROVEEDORES.items()]
        for future in as_completed(futures):
            nombre, resultado = future.result()
            if isinstance(resultado, str):
                status.set(resultado)
            else:
                all_data.extend(resultado)

    all_data.sort(key=lambda x: x["PrecioNum"])
    for row in all_data:
        del row["PrecioNum"]

    proveedor_box['values'] = ["Todos"] + sorted(set(item["Proveedor"] for item in all_data))
    proveedor_box.set("Todos")
    actualizar_filtro(tree, data_map, all_data, status, "Todos")

def lanzar_app():
    ventana = tk.Tk()
    ventana.title("🦷 Buscador Dental Multi-Proveedor")
    ventana.geometry("1400x800")

    top_frame = tk.Frame(ventana)
    top_frame.pack(pady=10)

    tk.Label(top_frame, text="Término a buscar:", font=("Segoe UI", 13)).pack(side=tk.LEFT, padx=5)
    entrada = tk.Entry(top_frame, width=40, font=("Segoe UI", 13))
    entrada.pack(side=tk.LEFT, padx=5)

    proveedor_box = ttk.Combobox(top_frame, state="readonly", width=20, font=("Segoe UI", 13))
    proveedor_box.pack(side=tk.LEFT, padx=5)

    data_map = {}
    all_data = []
    status_var = tk.StringVar()
    status_var.set("Introduce un término para buscar.")
    status_label = tk.Label(ventana, textvariable=status_var, anchor="w", font=("Segoe UI", 11))
    status_label.pack(fill=tk.X, padx=10)

    columns = ["Proveedor", "Nombre", "Precio Actual", "Precio Original", "Descuento", "Enlace"]
    tree = ttk.Treeview(ventana, columns=columns, show="headings", selectmode="browse")
    tree.pack(expand=True, fill='both', padx=10, pady=10)

    for col in columns:
        ancho = 500 if col == "Nombre" else 140
        tree.heading(col, text=col)
        tree.column(col, anchor="w", width=ancho)

    style = ttk.Style()
    style.configure("Treeview", font=("Segoe UI", 11), rowheight=30)
    style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))
    
    # Estilo para enlaces azules
    style.map("Treeview", foreground=[("!selected", "black")])
    style.configure("TreeviewEnlace.TLabel", foreground="blue", font=("Segoe UI", 11, "underline"))

    vsb = ttk.Scrollbar(ventana, orient="vertical", command=tree.yview)
    vsb.pack(side='right', fill='y')
    tree.configure(yscrollcommand=vsb.set)

    hsb = ttk.Scrollbar(ventana, orient="horizontal", command=tree.xview)
    hsb.pack(side='bottom', fill='x')
    tree.configure(xscrollcommand=hsb.set)

    boton = tk.Button(
        top_frame, text="🔍 Buscar", font=("Segoe UI", 12, "bold"),
        bg="#007acc", fg="white",
        command=lambda: ejecutar_busqueda(entrada.get(), tree, status_var, data_map, all_data, proveedor_box)
    )
    boton.pack(side=tk.LEFT, padx=5)

    proveedor_box.bind("<<ComboboxSelected>>", lambda e: actualizar_filtro(
        tree, data_map, all_data, status_var, proveedor_box.get()
    ))

    tree.bind("<Button-1>", lambda e: abrir_enlace(e, tree, data_map))
    tree.bind("<Motion>", lambda e: on_mouse_motion(e, tree))

    ventana.mainloop()

    
if __name__ == "__main__":
    lanzar_app()
