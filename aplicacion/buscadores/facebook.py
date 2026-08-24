"""Lee lo público de una página de Facebook.

Igual que Instagram: solo metadatos públicos. Sirve para confirmar que la
página existe y sacar el nombre y la descripción.
"""

import logging
import re

logger = logging.getLogger(__name__)


def _meta(pagina, propiedad: str) -> str | None:
    for elemento in pagina.css(f'meta[property="{propiedad}"]'):
        return elemento.attrib.get("content")
    return None


def leer(url: str) -> dict:
    if not url.startswith("http"):
        url = "https://www.facebook.com/" + url.strip().lstrip("/")

    resultado = {
        "facebook": url,
        "nombre": None,
        "descripcion": None,
        "existe": False,
        "logo_url": None,
    }

    try:
        from scrapling.fetchers import StealthyFetcher

        pagina = StealthyFetcher.fetch(url, headless=True)
    except Exception as error:  # noqa: BLE001
        logger.warning("No se pudo leer Facebook %s: %s", url, error)
        return resultado

    if pagina is None:
        return resultado

    resultado["nombre"] = _meta(pagina, "og:title")
    resultado["descripcion"] = _meta(pagina, "og:description")
    resultado["logo_url"] = _meta(pagina, "og:image")
    resultado["existe"] = bool(resultado["nombre"])
    return resultado


def url_desde_texto(texto: str) -> str | None:
    encontrado = re.search(r"https?://(?:www\.)?facebook\.com/[A-Za-z0-9.\-_/]+", texto or "")
    return encontrado.group(0) if encontrado else None
