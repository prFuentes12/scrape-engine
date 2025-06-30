from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scraper.utils import limpiar_texto
import time
import unicodedata

def normalizar(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', texto)
        if not unicodedata.combining(c)
    ).lower()

def buscar_tiendental(termino):
    print("⏳ Cargando página de TiendaDental...")

    url = f"https://tiendental.com/search?keyword={termino.replace(' ', '+')}"
    resultados = []

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    productos = soup.select("div.col.border-right.border-bottom")

    if not productos:
        print("⚠️ No se encontraron productos.")
        driver.quit()
        return []

    stopwords = {"de", "para", "con", "sin", "en", "el", "la", "los", "las", "un", "una"}
    terminos = [normalizar(t) for t in termino.lower().split() if t not in stopwords]

    for idx, prod in enumerate(productos, 1):
        try:
            nombre_el = prod.select_one("h3 a")
            if not nombre_el:
                continue

            nombre = limpiar_texto(nombre_el.text)
            nombre_normalizado = normalizar(nombre)
            nombre_tokens = [t for t in nombre_normalizado.split() if t not in stopwords]

            if not all(t in nombre_tokens for t in terminos):
                continue

            url_prod = nombre_el["href"]
            if not url_prod.startswith("http"):
                url_prod = "https://tiendental.com" + url_prod

            precio_el = prod.select_one("span.fw-700.text-primary.mx-auto")
            precio = limpiar_texto(precio_el.text) if precio_el else "-"

            original_el = prod.select_one("del.fw-400.text-secondary")
            precio_original = limpiar_texto(original_el.text) if original_el else "-"

            descuento_el = prod.select_one("span.absolute-top-left.bg-primary")
            descuento = limpiar_texto(descuento_el.text) if descuento_el else "-"

            resultados.append({
                "nombre": nombre,
                "precio": precio,
                "precio_original": precio_original,
                "descuento": descuento,
                "url": url_prod
            })

        except Exception as e:
            print(f"⚠️ Error en producto #{idx}: {e}")

    driver.quit()
    return resultados
