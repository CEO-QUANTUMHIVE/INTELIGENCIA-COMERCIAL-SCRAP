"""Lee lo público de un perfil de Instagram.

Instagram tapa casi todo detrás de login. Lo que se puede sacar sin cuenta es
la meta descripción del perfil (seguidores, publicaciones, bio). Alcanza para
saber si el negocio está activo en redes, que es lo único que necesitamos para
puntuar el prospecto.
"""

import logging
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

PATRON_NUMEROS = re.compile(
    r"([\d.,]+\s?[KMkm]?)\s+(?:seguidores|followers).*?"
    r"([\d.,]+\s?[KMkm]?)\s+(?:publicaciones|posts)",
    re.S | re.I,
)


def usuario_desde_url(url: str) -> str | None:
    encontrado = re.search(r"instagram\.com/([A-Za-z0-9._]+)", url or "")
    if not encontrado:
        return None
    usuario = encontrado.group(1)
    if usuario in ("p", "reel", "explore", "accounts"):
        return None
    return usuario


def _a_numero(texto: str) -> int | None:
    """'1,234' → 1234 | '1.2K' → 1200 | '3,5 M' → 3500000.

    Instagram usa coma o punto como separador de miles según el idioma, así que
    sin sufijo K/M sacamos todos los separadores; con sufijo, el separador que
    quede es decimal.
    """
    texto = texto.strip().replace(" ", "")
    if not texto:
        return None

    multiplicador = 1
    if texto[-1:].lower() == "k":
        multiplicador, texto = 1_000, texto[:-1]
    elif texto[-1:].lower() == "m":
        multiplicador, texto = 1_000_000, texto[:-1]

    if multiplicador == 1:
        texto = texto.replace(",", "").replace(".", "")
    else:
        texto = texto.replace(",", ".")

    try:
        return int(float(texto) * multiplicador)
    except ValueError:
        return None


def logo_de_perfil(valor: str | None) -> str | None:
    """Acepta fotos de perfil, no recursos genéricos de la interfaz de Meta."""
    if not valor:
        return None
    parsed = urlparse(valor)
    if parsed.scheme != "https" or not parsed.hostname:
        return None
    host = parsed.hostname.lower()
    if host == "static.cdninstagram.com":
        return None
    if host.endswith(".cdninstagram.com") and parsed.path.startswith("/rsrc.php"):
        return None
    return valor


def leer(url_o_usuario: str) -> dict:
    usuario = usuario_desde_url(url_o_usuario) or url_o_usuario.strip().lstrip("@")
    url = f"https://www.instagram.com/{usuario}/"
    resultado = {
        "instagram": url,
        "usuario": usuario,
        "seguidores": None,
        "publicaciones": None,
        "bio": None,
        "activo": None,
        "logo_url": None,
    }

    try:
        from scrapling.fetchers import StealthyFetcher

        pagina = StealthyFetcher.fetch(url, headless=True)
    except Exception as error:  # noqa: BLE001
        logger.warning("No se pudo leer Instagram de %s: %s", usuario, error)
        return resultado

    if pagina is None:
        return resultado

    descripcion = None
    for elemento in pagina.css('meta[property="og:description"]'):
        descripcion = elemento.attrib.get("content")
        break

    if not descripcion:
        return resultado

    encontrado = PATRON_NUMEROS.search(descripcion)
    if not encontrado:
        logger.info("Instagram no entregó metadatos públicos de %s", usuario)
        return resultado

    resultado["bio"] = descripcion
    resultado["seguidores"] = _a_numero(encontrado.group(1))
    resultado["publicaciones"] = _a_numero(encontrado.group(2))

    for elemento in pagina.css('meta[property="og:image"]'):
        resultado["logo_url"] = logo_de_perfil(elemento.attrib.get("content"))
        break

    seguidores = resultado["seguidores"] or 0
    publicaciones = resultado["publicaciones"] or 0
    resultado["activo"] = seguidores >= 300 and publicaciones >= 20

    return resultado
