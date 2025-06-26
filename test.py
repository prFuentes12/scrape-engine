from scraper.proclinic import buscar_proclinic

def imprimir_resultados(termino):
    resultados = buscar_proclinic(termino)
    print(f"\n🔍 Resultados para: '{termino}'\n")
    for idx, prod in enumerate(resultados, 1):
        print(f"{idx}. {prod['nombre']}")
        print(f"   Precio: {prod['precio']}")
        print(f"   Original: {prod['precio_original']}")
        print(f"   Descuento: {prod['descuento']}")
        print(f"   URL: {prod['url']}\n")

if __name__ == "__main__":
    imprimir_resultados("guantes de látex")
