from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import unicodedata

def normalizar(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', texto)
        if not unicodedata.combining(c)
    ).lower()

def buscar_100dental(termino):
    print("⏳ Cargando página de 100Dental...")

    url = f"https://www.100dental.es/?s={termino}&post_type=product&dgwt_wcas=1"
    resultados = []

    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    driver.get(url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    productos = soup.select('.product')

    if not productos:
        print("⚠️ No se encontraron productos.")
        driver.quit()
        return []

    stopwords = {"de", "para", "con", "sin", "en", "el", "la", "los", "las", "un", "una"}
    terminos = [normalizar(t) for t in termino.lower().split() if t not in stopwords]

    for idx, producto in enumerate(productos, 1):
        try:
            nombre_tag = producto.select_one('.wd-entities-title a')
            nombre = nombre_tag.get_text(strip=True) if nombre_tag else 'N/D'
            nombre_norm = normalizar(nombre)
            enlace = nombre_tag['href'] if nombre_tag and nombre_tag.has_attr('href') else ''

            if not all(t in nombre_norm for t in terminos):
                continue

            ins_tag = producto.select_one('ins .woocommerce-Price-amount.amount')
            del_tag = producto.select_one('del .woocommerce-Price-amount.amount')
            span_tags = producto.select('.woocommerce-Price-amount.amount')

            precio = None
            precio_original = None
            descuento = None

            if ins_tag and del_tag:
                precio = ins_tag.get_text(strip=True)
                precio_original = del_tag.get_text(strip=True)
                try:
                    pf = float(precio.replace(",", ".").replace("€", "").strip())
                    po = float(precio_original.replace(",", ".").replace("€", "").strip())
                    if po > pf:
                        descuento = f"-{round((1 - pf / po) * 100)}%"
                except:
                    descuento = None
            elif len(span_tags) == 2:
                precio_original = f"{span_tags[0].get_text(strip=True)}–{span_tags[1].get_text(strip=True)}"
            elif len(span_tags) == 1:
                precio_original = span_tags[0].get_text(strip=True)

            resultados.append({
                "nombre": nombre,
                "precio": precio,
                "precio_original": precio_original,
                "descuento": descuento,
                "url": enlace
            })

        except Exception as e:
            print(f"⚠️ Error en producto #{idx}: {e}")

    driver.quit()
    return resultados
