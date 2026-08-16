"""Encuentra decisores B2B (perfiles públicos de LinkedIn).

IMPORTANTE — leer antes de tocar este archivo:

LinkedIn prohíbe expresamente scrapear su sitio y bloquea/restringe las cuentas
que lo hacen. Así que acá NO entramos a linkedin.com: buscamos en un buscador
web los perfiles públicos que LinkedIn ya publicó e indexó, y nos quedamos con
nombre, cargo, empresa y la URL del perfil.

Después el resto del sistema investiga la empresa por su web, Maps y redes, que
es donde está la información que realmente sirve para armar la oferta.

Cuando haga falta volumen serio, la vía oficial es Sales Navigator + LinkedIn
Lead Gen Forms + Lead Sync API, y ese conector va acá al lado, no reemplazando
esto.
"""

import logging
import re
from urllib.parse import quote_plus, unquote

from aplicacion.modelos import Persona

logger = logging.getLogger(__name__)

BUSCADOR = "https://html.duckduckgo.com/html/?q="

# "Juan Pérez - CEO - Empresa X | LinkedIn"
PATRON_TITULO = re.compile(r"^(.*?)\s+[-–|]\s+(.*?)\s+[-–|]\s+(.*?)\s*(?:\|\s*LinkedIn)?$")


def _limpiar_url(href: str) -> str:
    """DuckDuckGo envuelve los resultados en un redirector."""
    encontrado = re.search(r"uddg=([^&]+)", href or "")
    return unquote(encontrado.group(1)) if encontrado else href


def buscar_decisores(
    rubro: str,
    ciudad: str | None = None,
    cargos: list[str] | None = None,
    cantidad: int = 20,
) -> list[Persona]:
    cargos = cargos or ["CEO", "dueño", "director", "fundador", "gerente"]
    partes = ['site:linkedin.com/in', f'"{rubro}"']
    if ciudad:
        partes.append(f'"{ciudad}"')
    partes.append("(" + " OR ".join(f'"{c}"' for c in cargos) + ")")
    consulta = " ".join(partes)

    logger.info("Buscando decisores: %s", consulta)

    try:
        from scrapling.fetchers import Fetcher

        pagina = Fetcher.get(BUSCADOR + quote_plus(consulta), impersonate="chrome")
    except Exception as error:  # noqa: BLE001
        logger.warning("No se pudo buscar decisores: %s", error)
        return []

    if pagina is None:
        return []

    # Dos listas paralelas: los href y los títulos, en el mismo orden.
    enlaces = [e.attrib.get("href", "") for e in pagina.css("a.result__a")]
    titulos = pagina.css("a.result__a::text").getall()

    personas: list[Persona] = []
    vistos: set[str] = set()

    for indice, href_crudo in enumerate(enlaces):
        href = _limpiar_url(href_crudo)
        if "linkedin.com/in/" not in href or href in vistos:
            continue
        vistos.add(href)

        titulo = (titulos[indice] if indice < len(titulos) else "").strip()
        if not titulo:
            continue

        nombre, cargo, empresa = titulo, None, None
        encontrado = PATRON_TITULO.match(titulo)
        if encontrado:
            nombre, cargo, empresa = (p.strip() for p in encontrado.groups())

        personas.append(
            Persona(
                nombre=nombre,
                cargo=cargo,
                empresa=empresa,
                linkedin=href.split("?")[0],
                ciudad=ciudad,
            )
        )
        if len(personas) >= cantidad:
            break

    logger.info("Decisores encontrados: %s", len(personas))
    return personas


def buscar_empresa(nombre_empresa: str) -> str | None:
    """Devuelve la URL pública de la página de empresa, si aparece."""
    consulta = f'site:linkedin.com/company "{nombre_empresa}"'
    try:
        from scrapling.fetchers import Fetcher

        pagina = Fetcher.get(BUSCADOR + quote_plus(consulta), impersonate="chrome")
    except Exception:  # noqa: BLE001
        return None

    if pagina is None:
        return None

    for elemento in pagina.css("a.result__a"):
        href = _limpiar_url(elemento.attrib.get("href", ""))
        if "linkedin.com/company/" in href:
            return href.split("?")[0]
    return None
