"""Lee lo público de un perfil de Instagram.

En producción usa un Actor de Apify desde el backend. Si no está configurado o
falla, conserva el lector público anterior como respaldo. Nunca recibe ni
guarda contraseñas, cookies o sesiones de Instagram.
"""

import logging
import re

import httpx

from aplicacion import configuracion

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


def normalizar_url(url_o_usuario: str) -> str:
    """Convierte URL, @usuario o usuario en la URL canónica del perfil."""
    usuario = usuario_desde_url(url_o_usuario) or url_o_usuario.strip().lstrip("@")
    return f"https://www.instagram.com/{usuario}/"


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


def _resultado_vacio(url_o_usuario: str) -> dict:
    url = normalizar_url(url_o_usuario)
    usuario = usuario_desde_url(url) or ""
    return {
        "instagram": url,
        "usuario": usuario,
        "seguidores": None,
        "publicaciones": None,
        "bio": None,
        "activo": None,
        "logo_url": None,
        "nombre": None,
        "web": None,
        "email": None,
        "categoria": None,
        "fuente": None,
    }


def _leer_apify(url_o_usuario: str) -> dict | None:
    """Ejecuta una sola consulta de detalles de perfil mediante Apify."""
    if not configuracion.hay_apify_instagram():
        return None

    url = normalizar_url(url_o_usuario)
    actor = configuracion.APIFY_INSTAGRAM_ACTOR.replace("/", "~")
    endpoint = (
        f"https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items"
    )
    respuesta = httpx.post(
        endpoint,
        headers={"Authorization": f"Bearer {configuracion.APIFY_TOKEN}"},
        json={"directUrls": [url], "resultsType": "details", "resultsLimit": 1},
        timeout=configuracion.APIFY_INSTAGRAM_TIMEOUT,
    )
    respuesta.raise_for_status()
    filas = respuesta.json()
    if not isinstance(filas, list) or not filas or not isinstance(filas[0], dict):
        return None

    fila = filas[0]
    if fila.get("error") or fila.get("ig_status") in {"not_found", "invalid_input"}:
        return None

    resultado = _resultado_vacio(url)
    resultado.update(
        {
            "instagram": fila.get("url") or url,
            "usuario": fila.get("username") or resultado["usuario"],
            "seguidores": fila.get("followersCount", fila.get("followers")),
            "publicaciones": fila.get("postsCount", fila.get("post_count")),
            "bio": fila.get("biography"),
            "logo_url": fila.get("profilePicUrlHD")
            or fila.get("profilePicUrl")
            or fila.get("profile_pic_url_hd")
            or fila.get("profile_pic_url"),
            "nombre": fila.get("fullName") or fila.get("full_name"),
            "web": fila.get("externalUrl") or fila.get("external_url"),
            "email": fila.get("businessEmail") or fila.get("contact_email"),
            "categoria": fila.get("businessCategoryName")
            or fila.get("categoryName"),
            "fuente": "apify",
        }
    )
    seguidores = resultado["seguidores"] or 0
    publicaciones = resultado["publicaciones"] or 0
    resultado["activo"] = seguidores >= 300 and publicaciones >= 20
    return resultado


def _leer_publico(url_o_usuario: str) -> dict:
    url = normalizar_url(url_o_usuario)
    usuario = usuario_desde_url(url) or ""
    resultado = _resultado_vacio(url)
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

    for elemento in pagina.css('meta[property="og:image"]'):
        resultado["logo_url"] = elemento.attrib.get("content")
        break

    descripcion = None
    for elemento in pagina.css('meta[property="og:description"]'):
        descripcion = elemento.attrib.get("content")
        break

    if not descripcion:
        return resultado

    resultado["bio"] = descripcion
    encontrado = PATRON_NUMEROS.search(descripcion)
    if encontrado:
        resultado["seguidores"] = _a_numero(encontrado.group(1))
        resultado["publicaciones"] = _a_numero(encontrado.group(2))

    seguidores = resultado["seguidores"] or 0
    publicaciones = resultado["publicaciones"] or 0
    resultado["activo"] = seguidores >= 300 and publicaciones >= 20
    resultado["fuente"] = "instagram_publico"

    return resultado


def leer(url_o_usuario: str) -> dict:
    """Prioriza Apify y degrada al lector público sin romper el onboarding."""
    try:
        resultado = _leer_apify(url_o_usuario)
        if resultado is not None:
            return resultado
    except Exception as error:  # noqa: BLE001
        logger.warning("Apify falló para %s: %s", url_o_usuario, error)

    return _leer_publico(url_o_usuario)
