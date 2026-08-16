"""Busca negocios en Google Maps.

Scrapea el listado y después entra a cada ficha para sacar teléfono y web,
que son los dos datos que realmente sirven para prospectar.
"""

import logging
import re
import time
from contextlib import contextmanager
from urllib.parse import quote_plus

from playwright.sync_api import Page, TimeoutError as ErrorDeEspera, sync_playwright

from aplicacion import configuracion
from aplicacion.modelos import Negocio

logger = logging.getLogger(__name__)

AGENTE = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


@contextmanager
def _navegador():
    with sync_playwright() as p:
        navegador = p.chromium.launch(
            headless=configuracion.NAVEGADOR_OCULTO,
            args=["--disable-blink-features=AutomationControlled", "--lang=es-AR"],
        )
        contexto = navegador.new_context(
            user_agent=AGENTE,
            locale="es-AR",
            viewport={"width": 1400, "height": 900},
        )
        pagina = contexto.new_page()
        try:
            yield pagina
        finally:
            contexto.close()
            navegador.close()


def _aceptar_cookies(pagina: Page) -> None:
    for selector in (
        'button[aria-label*="Aceptar"]',
        'button[aria-label*="Rechazar"]',
        'form[action*="consent"] button',
    ):
        try:
            boton = pagina.locator(selector).first
            if boton.is_visible(timeout=1500):
                boton.click(timeout=2000)
                pagina.wait_for_timeout(1000)
                return
        except Exception:  # noqa: BLE001
            continue


def _juntar_enlaces(pagina: Page, cantidad: int) -> list[str]:
    """Scrollea el panel de resultados hasta juntar `cantidad` fichas."""
    try:
        pagina.wait_for_selector('div[role="feed"]', timeout=20000)
    except ErrorDeEspera:
        logger.warning("Google Maps no mostró el listado de resultados.")
        return []

    feed = pagina.locator('div[role="feed"]')
    enlaces: list[str] = []
    sin_cambios = 0

    while len(enlaces) < cantidad and sin_cambios < 4:
        anteriores = len(enlaces)
        encontrados = pagina.eval_on_selector_all(
            'a[href*="/maps/place/"]',
            "elementos => elementos.map(e => e.href)",
        )
        enlaces = list(dict.fromkeys(encontrados))

        if len(enlaces) <= anteriores:
            sin_cambios += 1
        else:
            sin_cambios = 0

        try:
            feed.hover(timeout=5000)
            pagina.mouse.wheel(0, 3000)
        except Exception:  # noqa: BLE001
            # Si el panel desaparece o cambia, dejamos de scrollear y seguimos
            # con lo que ya juntamos en vez de tirar toda la búsqueda.
            break
        pagina.wait_for_timeout(1200)

    logger.info("Google Maps: %s fichas encontradas.", len(enlaces))
    return enlaces[:cantidad]


def _texto(pagina: Page, selector: str) -> str | None:
    try:
        elemento = pagina.locator(selector).first
        if elemento.count() == 0:
            return None
        valor = (elemento.inner_text(timeout=2500) or "").strip()
        return valor or None
    except Exception:  # noqa: BLE001
        return None


def _atributo(pagina: Page, selector: str, atributo: str) -> str | None:
    try:
        elemento = pagina.locator(selector).first
        if elemento.count() == 0:
            return None
        return elemento.get_attribute(atributo, timeout=2500)
    except Exception:  # noqa: BLE001
        return None


def _coordenadas(url: str) -> tuple[float | None, float | None]:
    encontrado = re.search(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", url)
    if encontrado:
        return float(encontrado.group(1)), float(encontrado.group(2))
    return None, None


def _leer_ficha(pagina: Page, url: str, ciudad: str) -> Negocio | None:
    try:
        pagina.goto(url, wait_until="domcontentloaded", timeout=30000)
        pagina.wait_for_selector("h1", timeout=15000)
    except ErrorDeEspera:
        logger.warning("No cargó la ficha: %s", url)
        return None

    nombre = _texto(pagina, "h1")
    if not nombre:
        return None

    puntuacion = None
    crudo = _texto(pagina, 'div.F7nice span[aria-hidden="true"]')
    if crudo:
        try:
            puntuacion = float(crudo.replace(",", "."))
        except ValueError:
            puntuacion = None

    resenas = None
    etiqueta = _atributo(pagina, "div.F7nice span[aria-label]", "aria-label")
    if etiqueta:
        numeros = re.sub(r"[^\d]", "", etiqueta)
        resenas = int(numeros) if numeros else None

    telefono = None
    id_telefono = _atributo(pagina, 'button[data-item-id^="phone:tel:"]', "data-item-id")
    if id_telefono:
        telefono = id_telefono.replace("phone:tel:", "").strip()

    direccion = None
    etiqueta_dir = _atributo(pagina, 'button[data-item-id="address"]', "aria-label")
    if etiqueta_dir:
        direccion = etiqueta_dir.split(":", 1)[-1].strip()

    web = _atributo(pagina, 'a[data-item-id="authority"]', "href")
    latitud, longitud = _coordenadas(pagina.url)

    return Negocio(
        nombre=nombre,
        categoria=_texto(pagina, 'button[jsaction*="category"]'),
        direccion=direccion,
        ciudad=ciudad,
        telefono=telefono,
        web=web,
        puntuacion_google=puntuacion,
        cantidad_resenas=resenas,
        url_maps=pagina.url,
        latitud=latitud,
        longitud=longitud,
    )


def buscar(rubro: str, ciudad: str, cantidad: int = 20) -> list[Negocio]:
    """Devuelve negocios de Google Maps para `rubro` en `ciudad`."""
    consulta = f"{rubro} en {ciudad}"
    url = f"https://www.google.com/maps/search/{quote_plus(consulta)}?hl=es"
    logger.info("Buscando en Google Maps: %s", consulta)

    negocios: list[Negocio] = []
    with _navegador() as pagina:
        pagina.goto(url, wait_until="domcontentloaded", timeout=45000)
        _aceptar_cookies(pagina)

        enlaces = _juntar_enlaces(pagina, cantidad)
        for indice, enlace in enumerate(enlaces, start=1):
            negocio = _leer_ficha(pagina, enlace, ciudad)
            if negocio:
                negocios.append(negocio)
                logger.info("  [%s/%s] %s", indice, len(enlaces), negocio.nombre)
            time.sleep(configuracion.PAUSA_ENTRE_NEGOCIOS)

    return negocios


def leer_una(url_maps: str, ciudad: str = "") -> Negocio | None:
    """Lee una sola ficha de Google Maps por URL."""
    with _navegador() as pagina:
        pagina.goto("https://www.google.com/maps?hl=es", wait_until="domcontentloaded")
        _aceptar_cookies(pagina)
        return _leer_ficha(pagina, url_maps, ciudad)
