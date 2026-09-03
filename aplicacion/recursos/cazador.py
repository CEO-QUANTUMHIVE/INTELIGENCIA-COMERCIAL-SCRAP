"""Cazador en vivo de oportunidades de financiamiento, créditos cloud y subsidios."""

import logging
import re
from urllib.parse import quote_plus, unquote
from aplicacion.modelos_recursos import CategoriaRecurso, Recurso, TipoCorreoRequerido

logger = logging.getLogger(__name__)

BUSCADOR = "https://html.duckduckgo.com/html/?q="


def _limpiar_url(href: str) -> str:
    """Extrae URL original del redirector de DuckDuckGo."""
    encontrado = re.search(r"uddg=([^&]+)", href or "")
    return unquote(encontrado.group(1)) if encontrado else href


def buscar_oportunidades_web(
    termino_busqueda: str = "creditos startups cloud aceleradora 2026",
    pais_o_region: str | None = None,
    cantidad: int = 10,
) -> list[Recurso]:
    """Busca en la web nuevas convocatorias, créditos y programas abiertos."""
    partes = [termino_busqueda]
    if pais_o_region:
        partes.append(f'"{pais_o_region}"')
    consulta = " ".join(partes)

    logger.info("Cazador buscando en la web: %s", consulta)

    resultados: list[Recurso] = []

    try:
        from scrapling.fetchers import Fetcher

        pagina = Fetcher.get(BUSCADOR + quote_plus(consulta), impersonate="chrome")
        elementos = pagina.css(".result")

        for idx, el in enumerate(elementos[:cantidad]):
            titulo_el = el.css_first(".result__title")
            snippet_el = el.css_first(".result__snippet")
            link_el = el.css_first(".result__url") or el.css_first(".result__title a")

            if not titulo_el:
                continue

            titulo = (titulo_el.text or "").strip()
            snippet = (snippet_el.text or "").strip() if snippet_el else ""
            href = link_el.attrib.get("href", "") if link_el else ""
            url_real = _limpiar_url(href)

            if not url_real or "duckduckgo.com" in url_real:
                continue

            # Detectar tipo de recurso y correo según palabras clave
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

            recurso_encontrado = Recurso(
                id=f"web-{idx}-{abs(hash(url_real)) % 100000}",
                nombre=titulo[:100],
                proveedor="Convocatoria / Web Externa",
                categoria=categoria,
                beneficio_principal=snippet[:180] or "Ver convocatoria oficial en el enlace",
                monto_estimado_usd=None,
                correo_requerido=correo_req,
                requisitos=["Consultar bases en el sitio oficial"],
                dificultad_aprobacion="Media",
                tiempo_respuesta="Variable",
                url_oficial=url_real,
                descripcion=snippet or titulo,
                instrucciones_postulacion=["Revisar enlace oficial para conocer fechas límite y requisitos."],
                tags=["cazador_web", categoria.value],
            )
            resultados.append(recurso_encontrado)

    except Exception as error:  # noqa: BLE001
        logger.warning("Fallo en búsqueda web del cazador: %s", error)

    return resultados
