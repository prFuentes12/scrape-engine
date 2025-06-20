from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scraper.utils import limpiar_texto
import time

def buscar_proclinic(termino):
    print("⏳ Cargando página de Proclinic...")

    url = f"https://www.proclinic.es/tienda/products/search?q={termino}"
    resultados = []

    options = Options()
    options.add_argument('--headless')  # Ejecuta en segundo plano
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # 🔐 Confirmar acceso como profesional
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='exclusive-professional-yes-button']"))
        ).click()
        print("✅ Confirmación de acceso aceptada.")
        time.sleep(2)
    except:
        print("ℹ️ No apareció el popup de confirmación.")

    # 🧼 Parsear con BeautifulSoup sin guardar HTML
    soup = BeautifulSoup(driver.page_source, "html.parser")
    cards = soup.select("div.product-card")

    if not cards:
        print("⚠️ No se encontraron productos.")
        driver.quit()
        return []

    for idx, card in enumerate(cards):
        try:
            nombre = card.select_one(".product-card__name a")
            precio_final = card.select_one(".product-card__price--final")
            precio_original = card.select_one(".product-card__price--regular")
            etiqueta = card.select_one(".product-card__offer")

            nombre_texto = limpiar_texto(nombre.text) if nombre else ''
            precio_texto = limpiar_texto(precio_final.text) if precio_final else ''
            original_texto = limpiar_texto(precio_original.text) if precio_original else ''
            etiqueta_texto = limpiar_texto(etiqueta.text) if etiqueta else None

            if termino.lower() not in nombre_texto.lower():
                continue

            resultados.append({
                "nombre": nombre_texto,
                "precio": precio_texto,
                "precio_original": original_texto or None,
                "descuento": etiqueta_texto or None
            })

        except Exception as e:
            print(f"⚠️ Error en producto #{idx + 1}: {e}")

    driver.quit()
    return resultados
