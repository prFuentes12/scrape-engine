from bs4 import BeautifulSoup
from selenium import webdriver  # type: ignore
from selenium.webdriver.chrome.options import Options  # type: ignore
from scraper.utils import limpiar_texto
import time
import unicodedata

def normalizar(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', texto)
        if not unicodedata.combining(c)
    ).lower()

def buscar_dentaltix(termino):
    print("⏳ Cargando página de Dentaltix...")

    url = f"https://www.dentaltix.com/es/search-results?keyword={termino.replace(' ', '+')}&_page=1"
    resultados = []

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    driver.get(url)

    # ⬇️ Scroll para cargar más productos dinámicamente
    SCROLL_PAUSES = 6
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(SCROLL_PAUSES):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    soup = BeautifulSoup(driver.page_source, "html.parser")
    productos = soup.select("div.product-item.product-model-item")

    stopwords = {"de", "para", "con", "sin", "en", "el", "la", "los", "las", "un", "una"}
    terminos = [normalizar(t) for t in termino.lower().split() if t not in stopwords]

    for idx, producto in enumerate(productos):
        try:
            nombre_tag = producto.select_one("a.product-item-title")
            precio_tag = producto.select_one("p.mini-price-container")
            tachado = precio_tag.select_one("del") if precio_tag else None

            nombre = limpiar_texto(nombre_tag.text) if nombre_tag else "N/D"
            nombre_normalizado = normalizar(nombre)

            if not all(t in nombre_normalizado for t in terminos):
                continue

            enlace = nombre_tag.get("href") if nombre_tag else ""
            if enlace and enlace.startswith("/"):
                enlace = "https://www.dentaltix.com" + enlace

            precio_original = limpiar_texto(tachado.text) if tachado else None

            precio_final = None
            if precio_tag:
                txt = limpiar_texto(precio_tag.get_text(separator=" ").strip())
                if precio_original:
                    precio_final = txt.replace(precio_original, "").strip()
                else:
                    precio_original = txt
                    precio_final = None

            descuento = None
            try:
                if precio_final and precio_original:
                    p = float(precio_final.replace(",", ".").replace("€", ""))
                    o = float(precio_original.replace(",", ".").replace("€", ""))
                    if o > p:
                        descuento = f"-{round((1 - p / o) * 100)}%"
            except:
                descuento = None

            resultados.append({
                "nombre": nombre,
                "precio": precio_final or "-",
                "precio_original": precio_original or "-",
                "descuento": descuento or "-",
                "url": enlace
            })

        except Exception as e:
            print(f"⚠️ Error en producto #{idx + 1}: {e}")

    driver.quit()
    return resultados
