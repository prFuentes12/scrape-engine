from scraper.brokerdental import buscar_producto

termino = "guantes"

print(f"🟦 Probando búsqueda en Broker Dental con término: '{termino}'")

try:
    resultados = buscar_producto(termino)
    print(f"🔍 {len(resultados)} resultados encontrados.\n")

    for idx, r in enumerate(resultados):
        print(f"{idx+1}. {r['nombre']} → {r['url']}")
except Exception as e:
    print(f"❌ Error: {e}")
