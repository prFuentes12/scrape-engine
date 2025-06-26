from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scraper.utils import limpiar_texto
import time
import unicodedata

def normalizar(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', texto)
        if not unicodedata.combining(c)
    ).lower()

def buscar_cliniclic(termino):
    print("⏳ Cargando página de Cliniclic...")
    url = f"https://cliniclic.com/catalogo-productos-dentales?term={termino.replace(' ', '%20')}"
    resultados = []

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    try:
        WebDriverWait(driver, 6).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'SÍ, SOY UN PROFESIONAL')]"))
        ).click()
        print("✅ Popup profesional aceptado.")
        time.sleep(2)
    except:
        print("⚠️ Popup profesional no detectado o falló.")

    try:
        WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Aceptar todo')]"))
        ).click()
        print("✅ Cookies aceptadas.")
        time.sleep(1)
    except:
        pass

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(4)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    productos = soup.select("article.c-mk-card")

    if not productos:
        print("⚠️ No se encontraron productos.")
        driver.quit()
        return []

    stopwords = {"de", "para", "con", "sin", "en", "el", "la", "los", "las", "un", "una"}
    terminos = [normalizar(t) for t in termino.lower().split() if t not in stopwords]

    for idx, prod in enumerate(productos, 1):
        try:
            nombre_el = prod.select_one("h1.c-mk-card__title")
            nombre = limpiar_texto(nombre_el.text) if nombre_el else "-"
            nombre_norm = normalizar(nombre)

            if not all(t in nombre_norm for t in terminos):
                continue

            url_el = prod.select_one("a.c-mk-card__link-product")
            url_prod = "https://cliniclic.com" + url_el["href"] if url_el else "-"

            precio_el = prod.select_one("h2.c-mk-card__price-title")
            precio = limpiar_texto(precio_el.text) if precio_el else "-"

            resultados.append({
                "nombre": nombre,
                "precio": precio,
                "precio_original": "-",
                "descuento": "-",
                "url": url_prod
            })

        except Exception as e:
            print(f"⚠️ Error en producto #{idx}: {e}")

    driver.quit()
    return resultados
