from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .utils import limpiar_texto
import unicodedata

def normalizar(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', texto)
        if not unicodedata.combining(c)
    ).lower()

def buscar_producto(nombre_busqueda):
    url = f"https://www.brokerdental.es/products/search?q={nombre_busqueda}&subfamilies=false"

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    print("⏳ Esperando resultados de búsqueda...")

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "products-catalog__item"))
        )
    except:
        print("⚠️ No se encontraron productos.")
        driver.quit()
        return []

    cards = driver.find_elements(By.CLASS_NAME, "products-catalog__item")
    resultados = []

    stopwords = {"de", "para", "con", "sin", "en", "el", "la", "los", "las", "un", "una"}
    terminos = [normalizar(t) for t in nombre_busqueda.lower().split() if t not in stopwords]

    for idx, card in enumerate(cards):
        try:
            nombre_el = card.find_elements(By.CSS_SELECTOR, "h3.product-card__name a")
            precio_el = card.find_elements(By.CSS_SELECTOR, "span.product-card__regular-price")
            original_el = card.find_elements(By.CSS_SELECTOR, "span.product-card__final-price-with-save")
            descuento_el = card.find_elements(By.CSS_SELECTOR, "p.product-card__save-percent")

            nombre = limpiar_texto(nombre_el[0].get_attribute("innerText")) if nombre_el else ''
            nombre_norm = normalizar(nombre)

            if not all(t in nombre_norm for t in terminos):
                continue

            enlace = nombre_el[0].get_attribute("href") if nombre_el else ''
            precio = limpiar_texto(precio_el[0].get_attribute("innerText")) if precio_el else ''
            precio_original = limpiar_texto(original_el[0].get_attribute("innerText")) if original_el else ''
            descuento = limpiar_texto(descuento_el[0].get_attribute("innerText")) if descuento_el else None

            resultados.append({
                "nombre": nombre,
                "precio": precio,
                "precio_original": precio_original,
                "descuento": descuento,
                "url": enlace
            })
        except Exception as e:
            print(f"⚠️ Error en producto #{idx + 1}: {e}")

    driver.quit()
    return resultados
