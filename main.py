from tabulate import tabulate

# 🟩 Elige aquí el proveedor que quieres usar (descomenta uno):
# from scraper.brokerdental import buscar_broker_dental as buscar_producto
# from scraper.dentaliberica import buscar_dentaliberica as buscar_producto
# from scraper.proclinic import buscar_proclinic as buscar_producto
from scraper.dentaltix import buscar_dentaltix as buscar_producto

if __name__ == "__main__":
    termino = "guante"

    productos = buscar_producto(termino)

    proveedor = buscar_producto.__name__.replace("buscar_", "").replace("_", " ").title()

    print(f"\n🔎 RESULTADOS PARA: '{termino.upper()}' en {proveedor}")
    tabla = [
        [
            prod["nombre"],
            prod["precio"],
            prod["precio_original"] if prod["precio_original"] else "-",
            prod["descuento"] if prod["descuento"] else "-"
        ]
        for prod in productos
    ]
    print(tabulate(tabla, headers=["Nombre", "Precio", "Original", "Descuento"], tablefmt="grid"))
