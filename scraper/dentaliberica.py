from playwright.sync_api import sync_playwright
from scraper.utils import limpiar_texto

def buscar_dentaliberica(termino):
    url = f"https://dentaliberica.com/es/products/search?q={termino}&subfamilies=true"
    resultados = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        print("⏳ Esperando a que cargue la página...")

        try:
            page.wait_for_selector("div.product-card", timeout=15000)
        except:
            print("⚠️ No se detectó el contenedor de productos.")
            browser.close()
            return []

        cards = page.query_selector_all("div.product-card")

        for idx, card in enumerate(cards):
            try:
                nombre_el = card.query_selector("div.product-card__name a")
                if not nombre_el:
                    continue
                nombre = limpiar_texto(nombre_el.inner_text())

                # Reconstruir el precio final
                precio_final_el = card.query_selector("span.product-card__price--final")
                if precio_final_el:
                    entero = precio_final_el.query_selector("span.integer-part")
                    decimal = precio_final_el.query_selector("span.decimal-part")
                    moneda = precio_final_el.query_selector("span.currency-part")

                    precio = f"{entero.inner_text().strip() if entero else ''}{decimal.inner_text().strip() if decimal else ''}{moneda.inner_text().strip() if moneda else ''}"
                else:
                    precio = ''

                # Precio original (si lo hubiera)
                precio_orig_el = card.query_selector("span.product-card__price--before")
                precio_original = limpiar_texto(precio_orig_el.inner_text()) if precio_orig_el else ''

                # Etiqueta (como descuento, liquidación, etc)
                etiqueta_el = card.query_selector("span.badge")
                descuento = limpiar_texto(etiqueta_el.inner_text()) if etiqueta_el else None

                resultados.append({
                    "nombre": nombre,
                    "precio": precio,
                    "precio_original": precio_original,
                    "descuento": descuento
                })

            except Exception as e:
                print(f"⚠️ Error en producto #{idx + 1}: {e}")

        browser.close()
    return resultados
