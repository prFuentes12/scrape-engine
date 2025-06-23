import tkinter as tk
from tkinter import messagebox
from tabulate import tabulate

# Importa todos los scrapers
from scraper.brokerdental import buscar_producto
from scraper.dentaliberica import buscar_dentaliberica
from scraper.proclinic import buscar_proclinic
from scraper.dentaltix import buscar_dentaltix
from scraper.dentalexpress import buscar_dentalexpress
from scraper.ciendental import buscar_100dental

# Diccionario de funciones por proveedor
PROVEEDORES = {
    "Broker Dental": buscar_producto,
    "Dental Ibérica": buscar_dentaliberica,
    "Proclinic": buscar_proclinic,
    "Dentaltix": buscar_dentaltix,
    "Dental Express": buscar_dentalexpress,
    "100Dental": buscar_100dental
}

# Convierte precio string a float para ordenar (solo primer número si es rango)
def convertir_precio(precio_str):
    try:
        if not precio_str or precio_str == "-":
            return float('inf')
        parte = precio_str.split("–")[0].replace("€", "").replace(",", ".").strip()
        return float(parte)
    except:
        return float('inf')


def aplicar_colores(output_box, tabla_str):
    output_box.insert(tk.END, tabla_str + "\n")

    lines = tabla_str.splitlines()
    for i, line in enumerate(lines):
        if i == 2:  # fila de headers
            output_box.tag_add("cabecera", f"{i+1}.0", f"{i+1}.end")
        elif i > 2:
            output_box.tag_add("col0", f"{i+1}.2", f"{i+1}.22")   # Proveedor
            output_box.tag_add("col1", f"{i+1}.25", f"{i+1}.85")  # Nombre
            output_box.tag_add("col2", f"{i+1}.88", f"{i+1}.106") # Precio
            output_box.tag_add("col3", f"{i+1}.109", f"{i+1}.127")# Original
            output_box.tag_add("col4", f"{i+1}.130", f"{i+1}.end")# Descuento


from concurrent.futures import ThreadPoolExecutor, as_completed

def ejecutar_busqueda(termino, output_box):
    if not termino.strip():
        messagebox.showwarning("Campo vacío", "Por favor ingresa un término de búsqueda.")
        return

    tabla_final = []
    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, f"🔎 Buscando '{termino}' en todos los proveedores...\n\n")
    output_box.update()

    def ejecutar_scraper(nombre, funcion):
        try:
            productos = funcion(termino)
            resultado = []
            for prod in productos:
                resultado.append({
                    "Proveedor": nombre,
                    "Nombre": prod.get("nombre", "N/D"),
                    "Precio Descuento": prod.get("precio") or "-",
                    "Precio Original": prod.get("precio_original") or "-",
                    "Descuento": prod.get("descuento") or "-",
                    "PrecioNum": convertir_precio(prod.get("precio") or prod.get("precio_original") or "")
                })
            return (nombre, resultado)
        except Exception as e:
            return (nombre, f"❌ Error con {nombre}: {e}")

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(ejecutar_scraper, nombre, func) for nombre, func in PROVEEDORES.items()]

        for future in as_completed(futures):
            nombre, resultado = future.result()
            if isinstance(resultado, str):  # Es un mensaje de error
                output_box.insert(tk.END, resultado + "\n")
            else:
                tabla_final.extend(resultado)
                output_box.insert(tk.END, f"✅ {nombre} completado ({len(resultado)} productos)\n")
            output_box.update()

    tabla_ordenada = sorted(tabla_final, key=lambda x: x["PrecioNum"])
    for row in tabla_ordenada:
        del row["PrecioNum"]

    if tabla_ordenada:
        output_box.insert(tk.END, "\n🔎 RESULTADOS ORDENADOS POR PRECIO:\n\n")
        tabla_str = tabulate(tabla_ordenada, headers="keys", tablefmt="grid")
        aplicar_colores(output_box, tabla_str)
    else:
        output_box.insert(tk.END, "\n⚠️ No se encontraron resultados.\n")



def lanzar_app():
    ventana = tk.Tk()
    ventana.title("🦷 Buscador Dental Multi-Proveedor")
    ventana.geometry("1380x880")
    ventana.configure(bg="#f0f0f0")

    # 🔹 Entrada y botón
    frame_superior = tk.Frame(ventana, bg="#f0f0f0")
    frame_superior.pack(pady=10)

    label = tk.Label(frame_superior, text="Término a buscar:", font=("Segoe UI", 12), bg="#f0f0f0")
    label.pack(side=tk.LEFT, padx=5)

    entrada = tk.Entry(frame_superior, width=40, font=("Segoe UI", 12))
    entrada.pack(side=tk.LEFT, padx=5)

    boton = tk.Button(
        frame_superior,
        text="🔍 Buscar",
        font=("Segoe UI", 12, "bold"),
        bg="#007acc",
        fg="white",
        activebackground="#005f99",
        activeforeground="white",
        command=lambda: ejecutar_busqueda(entrada.get(), output_box)
    )
    boton.pack(side=tk.LEFT, padx=5)

    # 🔹 Contenedor con Scrollbars y Text
    frame_texto = tk.Frame(ventana)
    frame_texto.pack(expand=True, fill="both", padx=10, pady=10)

    y_scroll = tk.Scrollbar(frame_texto)
    y_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    x_scroll = tk.Scrollbar(frame_texto, orient='horizontal')
    x_scroll.pack(side=tk.BOTTOM, fill=tk.X)

    output_box = tk.Text(
        frame_texto,
        wrap="none",
        font=("Courier New", 10),
        bg="#ffffff",
        yscrollcommand=y_scroll.set,
        xscrollcommand=x_scroll.set
    )
    output_box.pack(side=tk.LEFT, expand=True, fill="both")

    y_scroll.config(command=output_box.yview)
    x_scroll.config(command=output_box.xview)

    # 🔹 Estilos de columnas
    output_box.tag_config("cabecera", background="#007acc", foreground="white", font=("Courier New", 10, "bold"))
    output_box.tag_config("col0", foreground="#005f99")   # Proveedor
    output_box.tag_config("col1", foreground="#333333")   # Nombre
    output_box.tag_config("col2", foreground="#0a9c20")   # Precio descuento
    output_box.tag_config("col3", foreground="#8c7500")   # Precio original
    output_box.tag_config("col4", foreground="#cc0000")   # Descuento

    ventana.mainloop()

if __name__ == "__main__":
    lanzar_app()