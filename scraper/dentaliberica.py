from playwright.sync_api import sync_playwright
from scraper.utils import limpiar_texto
import unicodedata

def normalizar(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', texto)
        if not unicodedata.combining(c)
    ).lower()

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

        stopwords = {"de", "para", "con", "sin", "en", "el", "la", "los", "las", "un", "una"}
        terminos = [normalizar(t) for t in termino.lower().split() if t not in stopwords]

        for idx, card in enumerate(cards):
            try:
                nombre_el = card.query_selector("div.product-card__name a")
                if not nombre_el:
                    continue

                nombre = limpiar_texto(nombre_el.inner_text())
                nombre_norm = normalizar(nombre)

                if not all(t in nombre_norm for t in terminos):
                    continue

                enlace = nombre_el.get_attribute("href")
                url_producto = f"https://dentaliberica.com{enlace}" if enlace and enlace.startswith("/") else enlace

                # Precio final
                precio_final_el = card.query_selector("span.product-card__price--final")
                if precio_final_el:
                    entero = precio_final_el.query_selector("span.integer-part")
                    decimal = precio_final_el.query_selector("span.decimal-part")
                    moneda = precio_final_el.query_selector("span.currency-part")
                    precio = f"{entero.inner_text().strip() if entero else ''}{decimal.inner_text().strip() if decimal else ''}{moneda.inner_text().strip() if moneda else ''}"
                else:
                    precio = ''

                # Precio original
                precio_orig_el = card.query_selector("span.product-card__price--before")
                precio_original = limpiar_texto(precio_orig_el.inner_text()) if precio_orig_el else ''

                # Descuento o etiqueta
                etiqueta_el = card.query_selector("span.badge")
                descuento = limpiar_texto(etiqueta_el.inner_text()) if etiqueta_el else None

                resultados.append({
                    "nombre": nombre,
                    "precio": precio,
                    "precio_original": precio_original,
                    "descuento": descuento,
                    "url": url_producto
                })

            except Exception as e:
                print(f"⚠️ Error en producto #{idx + 1}: {e}")

        browser.close()
    return resultados
