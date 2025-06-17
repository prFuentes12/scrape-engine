def limpiar_texto(texto):
    """Limpia saltos de línea, espacios extra, etc."""
    return texto.strip().replace('\n', ' ')


def capturar_estado(driver, nombre):
    html = driver.page_source
    with open(f"{nombre}_debug.html", "w", encoding="utf-8") as f:
        f.write(html)
    driver.save_screenshot(f"{nombre}_error.png")
