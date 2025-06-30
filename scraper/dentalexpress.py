from bs4 import BeautifulSoup
from selenium import webdriver # type: ignore
from selenium.webdriver.chrome.options import Options # type: ignore
from selenium.webdriver.common.by import By # type: ignore 
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.support import expected_conditions as EC # type: ignore
import time
import unicodedata

def normalizar(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFKD', texto)
        if not unicodedata.combining(c)
    ).lower()

def buscar_dentalexpress(termino):
    print("⏳ Cargando página de DentalExpress...")

    url = f"https://dentalexpress.es/#df08/fullscreen/m=and&q={termino}"
    resultados = []

    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "usercentrics-root"))
        )
        print("✅ Overlay de cookies cerrado.")
    except:
        print("⚠️ Overlay de cookies no desapareció.")

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "professional-input-custom"))
        )
        driver.execute_script("document.getElementById('professional-input-custom').click();")
        time.sleep(1)
        driver.execute_script("""
            [...document.querySelectorAll("button")].forEach(btn => {
                if (btn.textContent.includes("ACEPTAR")) btn.click();
            });
        """)
        print("✅ Confirmación como profesional aceptada (con JS).")
        time.sleep(3)
    except Exception as e:
        print(f"⚠️ No se pudo aceptar el popup: {e}")

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    productos = soup.select('.dfd-card-content.dfd-card-flex')

    if not productos:
        print("⚠️ No se encontraron productos.")
    else:
        print(f"✅ {len(productos)} producto(s) encontrados:\n")

        stopwords = {"de", "para", "con", "sin", "en", "el", "la", "los", "las", "un", "una"}
        terminos = [normalizar(t) for t in termino.lower().split() if t not in stopwords]

        for idx, producto in enumerate(productos, 1):
            try:
                nombre_el = producto.select_one('.dfd-card-title')
                nombre = nombre_el.get_text(strip=True) if nombre_el else 'N/D'
                nombre_norm = normalizar(nombre)

                if not all(t in nombre_norm for t in terminos):
                    continue

                link_el = producto.find_parent('div', class_='dfd-card')
                link = link_el.get("dfd-value-link") if link_el else None

                precio_sale = producto.select_one('.dfd-card-price.dfd-card-price--sale')
                precio_regular = producto.select_one('.dfd-card-price:not(.dfd-card-price--sale)')

                precio = precio_sale.get_text(strip=True) if precio_sale else None
                precio_original = precio_regular.get_text(strip=True) if precio_regular else None

                if precio_regular and precio_sale:
                    precio_final = precio
                elif precio_regular:
                    precio_final = precio_original
                    precio_original = None
                else:
                    precio_final = "N/D"
                    precio_original = None

                descuento = None
                try:
                    if precio_original and precio_final:
                        po = float(precio_original.replace(",", ".").replace("€", "").strip())
                        pf = float(precio_final.replace(",", ".").replace("€", "").strip())
                        if po > pf:
                            descuento = f"-{round((1 - pf / po) * 100)}%"
                except:
                    pass

                resultados.append({
                    "nombre": nombre,
                    "precio": precio_final,
                    "precio_original": precio_original,
                    "descuento": descuento,
                    "url": f"{link}" if link else None
                })

            except Exception as e:
                print(f"⚠️ Error en producto #{idx}: {e}")

    driver.quit()
    return resultados
