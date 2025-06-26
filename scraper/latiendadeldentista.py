from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unicodedata
import time

def limpiar_texto(texto):
    return " ".join(texto.strip().replace("\n", " ").split())

def normalizar(texto):
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8").lower()

def buscar_latiendadeldentista(termino):
    print("⏳ Cargando página de La Tienda del Dentista...")

    url = f"https://www.latiendadeldentista.com/buscar?controller=search&s={termino.replace(' ', '+')}"
    resultados = []

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "products"))
        )
    except:
        print("⚠️ No se detectó el contenedor de productos.")
        driver.quit()
        return []

    soup = BeautifulSoup(driver.page_source, "html.parser")
    productos = soup.select("article.ajax_block_product")

    stopwords = {"de", "para", "con", "sin", "en", "el", "la", "los", "las", "un", "una"}
    terminos = [normalizar(t) for t in termino.lower().split() if t not in stopwords]

    for idx, prod in enumerate(productos, 1):
        try:
            nombre_el = prod.select_one("h3.s_title_block a")
            nombre = limpiar_texto(nombre_el.text) if nombre_el else "-"
            if not all(t in normalizar(nombre).lower() for t in terminos):
                continue

            url = nombre_el["href"] if nombre_el else "-"

            precio = "-"
            original = "-"
            descuento = "-"

            precio_el = prod.select_one("span.price.st_discounted_price")
            if precio_el:
                precio = limpiar_texto(precio_el.text)

            original_el = prod.select_one("span.regular-price")
            if original_el:
                original = limpiar_texto(original_el.text)

            descuento_el = prod.select_one("span.cuantomenos.discount.discount-amount")
            if descuento_el:
                descuento = limpiar_texto(descuento_el.text)

            resultados.append({
                "nombre": nombre,
                "precio": precio,
                "precio_original": original,
                "descuento": descuento,
                "url": url
            })

        except Exception as e:
            print(f"⚠️ Error en producto #{idx}: {e}")

    driver.quit()
    return resultados
