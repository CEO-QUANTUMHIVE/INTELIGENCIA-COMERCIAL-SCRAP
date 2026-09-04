"""Cazador en vivo de oportunidades de financiamiento, créditos y subsidios."""

import hashlib
import logging
import re
from urllib.parse import quote_plus, unquote, urlparse

import httpx

from aplicacion import configuracion
from aplicacion.modelos_recursos import CategoriaRecurso, Recurso, TipoCorreoRequerido

logger = logging.getLogger(__name__)

BUSCADOR = "https://html.duckduckgo.com/html/?q="


def _limpiar_url(href: str) -> str:
    """Extrae URL original del redirector de DuckDuckGo."""
    encontrado = re.search(r"uddg=([^&]+)", href or "")
    return unquote(encontrado.group(1)) if encontrado else href


def _crear_recurso(
    titulo: str,
    snippet: str,
    url: str,
    fuente: str,
) -> Recurso | None:
    """Normaliza un resultado de buscador al contrato público de recursos."""
    titulo = (titulo or "").strip()
    snippet = (snippet or "").strip()
    url = _limpiar_url((url or "").strip())
    parsed = urlparse(url)
    if not titulo or parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    if "duckduckgo.com" in parsed.netloc.lower():
        return None

    texto_completo = f"{titulo} {snippet}".lower()
    categoria = CategoriaRecurso.SUBSIDIO
    if any(k in texto_completo for k in ["aws", "azure", "google cloud", "cloud", "hosting", "vps"]):
        categoria = CategoriaRecurso.CLOUD
    elif any(k in texto_completo for k in ["ia", "ai", "nvidia", "openai", "machine learning"]):
        categoria = CategoriaRecurso.AI_STARTUP
    elif any(k in texto_completo for k in ["estudiante", "universidad", "education", "student", ".edu"]):
        categoria = CategoriaRecurso.EDUCATIVO
    elif any(k in texto_completo for k in ["github", "developer", "api", "database"]):
        categoria = CategoriaRecurso.DEV_TOOLS

    correo_req = TipoCorreoRequerido.CUALQUIERA
    if ".edu" in texto_completo or "estudiante" in texto_completo:
        correo_req = TipoCorreoRequerido.ESTUDIANTE
    elif any(k in texto_completo for k in ["startup", "empresa", "corporativo", "founders"]):
        correo_req = TipoCorreoRequerido.CORPORATIVO

    identificador = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
    return Recurso(
        id=f"web-{identificador}",
        nombre=titulo[:100],
        proveedor=fuente,
        categoria=categoria,
        beneficio_principal=snippet[:180] or "Ver convocatoria oficial en el enlace",
        monto_estimado_usd=None,
        correo_requerido=correo_req,
        requisitos=["Consultar bases en el sitio oficial"],
        dificultad_aprobacion="Media",
        tiempo_respuesta="Variable",
        url_oficial=url,
        descripcion=snippet or titulo,
        instrucciones_postulacion=[
            "Revisar el enlace oficial para confirmar vigencia, fechas límite y requisitos."
        ],
        tags=["cazador_web", categoria.value],
    )


def _buscar_con_apify(consulta: str, cantidad: int) -> list[Recurso]:
    """Consulta una página del Actor oficial de Google Search en Apify."""
    actor = configuracion.APIFY_BUSQUEDA_ACTOR.replace("/", "~")
    endpoint = f"https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items"
    respuesta = httpx.post(
        endpoint,
        headers={"Authorization": f"Bearer {configuracion.APIFY_TOKEN}"},
        params={
            "timeout": int(configuracion.APIFY_BUSQUEDA_TIMEOUT),
            "maxItems": 1,
            "maxTotalChargeUsd": configuracion.APIFY_BUSQUEDA_MAX_COSTO_USD,
        },
        json={
            "queries": consulta,
            "maxPagesPerQuery": 1,
            "languageCode": "es",
            "saveHtmlToKeyValueStore": False,
            "includeIcons": False,
        },
        timeout=configuracion.APIFY_BUSQUEDA_TIMEOUT,
    )
    respuesta.raise_for_status()
    filas = respuesta.json()
    if not isinstance(filas, list):
        return []

    candidatos: list[dict] = []
    for fila in filas:
        if not isinstance(fila, dict):
            continue
        organicos = fila.get("organicResults")
        if isinstance(organicos, list):
            candidatos.extend(item for item in organicos if isinstance(item, dict))
        elif fila.get("url") or fila.get("link"):
            candidatos.append(fila)

    resultados: list[Recurso] = []
    urls_vistas: set[str] = set()
    for item in candidatos:
        url = item.get("url") or item.get("link") or ""
        if url in urls_vistas:
            continue
        recurso = _crear_recurso(
            item.get("title") or item.get("name") or "",
            item.get("description") or item.get("snippet") or item.get("text") or "",
            url,
            "Google Search / Apify",
        )
        if recurso is None:
            continue
        urls_vistas.add(url)
        resultados.append(recurso)
        if len(resultados) >= cantidad:
            break
    return resultados


def _buscar_con_duckduckgo(consulta: str, cantidad: int) -> list[Recurso]:
    """Respaldo gratuito cuando Apify no está configurado o no responde."""
    from scrapling.fetchers import Fetcher

    pagina = Fetcher.get(BUSCADOR + quote_plus(consulta), impersonate="chrome")
    elementos = pagina.css(".result")
    resultados: list[Recurso] = []
    for elemento in elementos:
        titulo_el = elemento.css_first(".result__title")
        snippet_el = elemento.css_first(".result__snippet")
        link_el = elemento.css_first(".result__url") or elemento.css_first(".result__title a")
        recurso = _crear_recurso(
            (titulo_el.text or "") if titulo_el else "",
            (snippet_el.text or "") if snippet_el else "",
            link_el.attrib.get("href", "") if link_el else "",
            "DuckDuckGo",
        )
        if recurso is not None:
            resultados.append(recurso)
        if len(resultados) >= cantidad:
            break
    return resultados


def buscar_oportunidades_web(
    termino_busqueda: str = "creditos startups cloud aceleradora 2026",
    pais_o_region: str | None = None,
    cantidad: int = 10,
) -> list[Recurso]:
    """Busca nuevas convocatorias; prioriza Apify y conserva un respaldo web."""
    cantidad = max(1, min(cantidad, 25))
    partes = [termino_busqueda]
    if pais_o_region:
        partes.append(f'"{pais_o_region}"')
    consulta = " ".join(partes)
    logger.info("Cazador buscando en la web: %s", consulta)

    if configuracion.hay_apify_busqueda():
        try:
            resultados = _buscar_con_apify(consulta, cantidad)
            if resultados:
                return resultados
            logger.warning("Apify no devolvió resultados para el cazador; uso respaldo.")
        except Exception as error:  # noqa: BLE001
            logger.warning("Apify falló para el cazador; uso respaldo: %s", error)

    try:
        return _buscar_con_duckduckgo(consulta, cantidad)
    except Exception as error:  # noqa: BLE001
        logger.warning("Fallo también el respaldo DuckDuckGo del cazador: %s", error)
        return []
