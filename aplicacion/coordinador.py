"""El Coordinador de Investigación.

Un solo agente con herramientas. Cuando haya volumen de verdad, lo partimos
en varios. Hoy no hace falta.
"""

import logging

from aplicacion.base_datos import supabase
from aplicacion.buscadores import facebook, google_maps, instagram, linkedin, web
from aplicacion.enriquecimiento import negocio as enriquecedor
from aplicacion.enriquecimiento import oportunidades, visual
from aplicacion.ia import perfil_cliente
from aplicacion.modelos import (
    Negocio,
    NegocioAnalizado,
    PaquetePerfilCliente,
    Persona,
)
from aplicacion.modelos_recursos import (
    FiltroRecursos,
    PeticionPostulacion,
    Recurso,
    RespuestaPostulacion,
)
from aplicacion.recursos import (
    buscar_oportunidades_web,
    filtrar_recursos,
    generar_postulacion,
    obtener_recurso,
)

logger = logging.getLogger(__name__)


# ─── Flujo A: buscar clientes nuevos ─────────────────────────────────


def buscar_negocios(
    rubro: str,
    ciudad: str,
    cantidad: int = 20,
    analizar: bool = True,
    guardar: bool = True,
) -> list[NegocioAnalizado]:
    """«Buscá 30 barberías de Buenos Aires que puedan necesitar web y agente IA.»"""

    logger.info("=== Buscando %s %s en %s ===", cantidad, rubro, ciudad)

    encontrados = google_maps.buscar(rubro, ciudad, cantidad)
    if not encontrados:
        logger.warning("Google Maps no devolvió resultados.")
        return []

    enriquecidos = enriquecedor.enriquecer_lote(encontrados)

    if analizar:
        pares = oportunidades.analizar_lote(enriquecidos)
        resultados = [NegocioAnalizado(negocio=n, analisis=a) for n, a in pares]
    else:
        resultados = [NegocioAnalizado(negocio=n) for n in enriquecidos]

    if guardar:
        for resultado in resultados:
            try:
                supabase.guardar_negocio(resultado.negocio, resultado.analisis)
            except Exception as error:  # noqa: BLE001
                logger.error("No se pudo guardar %s: %s", resultado.negocio.nombre, error)
        supabase.registrar_investigacion(
            "prospeccion",
            {"rubro": rubro, "ciudad": ciudad, "cantidad": cantidad},
            len(resultados),
        )

    logger.info("=== Listo: %s negocios ===", len(resultados))
    return resultados


# ─── Flujo B: investigar un negocio puntual ──────────────────────────


def investigar_negocio(
    nombre: str | None = None,
    web_url: str | None = None,
    instagram_url: str | None = None,
    facebook_url: str | None = None,
    url_maps: str | None = None,
    guardar: bool = True,
) -> NegocioAnalizado:
    """«Investigá Yaspapeobeauty» — con lo que tengas: nombre, web, IG o Maps."""

    base: Negocio | None = None

    if url_maps:
        base = google_maps.leer_una(url_maps)

    if base is None:
        base = Negocio(
            nombre=nombre or web.dominio(web_url or "") or "Sin nombre",
            web=web_url,
            instagram=instagram_url,
            facebook=facebook_url,
        )
    else:
        base.web = base.web or web_url
        base.instagram = base.instagram or instagram_url
        base.facebook = base.facebook or facebook_url

    completo = enriquecedor.enriquecer(base)
    analisis = oportunidades.analizar(completo)

    if guardar:
        negocio_id = supabase.guardar_negocio(completo, analisis)
        if negocio_id and completo.web:
            supabase.guardar_fuente(negocio_id, "web", completo.web, {})

    return NegocioAnalizado(negocio=completo, analisis=analisis)


# ─── Flujo C: paquete para Fábrica de Webs y Fábrica de Agentes ──────


def investigar_cliente(
    nombre: str,
    web_url: str | None = None,
    instagram_url: str | None = None,
    facebook_url: str | None = None,
    url_maps: str | None = None,
) -> PaquetePerfilCliente:
    """Onboarding de un cliente que ya contrató.

    Devuelve el paquete que consumen la Fábrica de Webs y la de Agentes:
    datos del negocio, marca, y (vía IA sobre lo scrapeado) servicios,
    precios, horarios, preguntas frecuentes y competidores mencionados.
    """

    resultado = investigar_negocio(
        nombre=nombre,
        web_url=web_url,
        instagram_url=instagram_url,
        facebook_url=facebook_url,
        url_maps=url_maps,
        guardar=False,
    )
    ficha = resultado.negocio

    datos_ig = {}
    if ficha.instagram:
        try:
            datos_ig = instagram.leer(ficha.instagram)
        except Exception:  # noqa: BLE001
            datos_ig = {}

    datos_fb = {}
    if ficha.facebook:
        try:
            datos_fb = facebook.leer(ficha.facebook)
        except Exception:  # noqa: BLE001
            datos_fb = {}

    perfil = perfil_cliente.extraer(
        {
            "nombre": ficha.nombre,
            "categoria": ficha.categoria,
            "texto_web": ficha.texto_web,
            "bio_instagram": datos_ig.get("bio"),
            "descripcion_facebook": datos_fb.get("descripcion"),
        }
    )

    # Prioridad: el logo de la propia web (más confiable) > el de Instagram
    # > el de Facebook. Es una URL pública, no se descarga ni se re-hostea.
    logo_url = ficha.logo_url or datos_ig.get("logo_url") or datos_fb.get("logo_url")
    ficha.logo_url = logo_url
    colores = visual.extraer_colores(logo_url)

    paquete = PaquetePerfilCliente(
        negocio=ficha,
        servicios=perfil["servicios"],
        precios=perfil["precios"],
        horarios=perfil["horarios"],
        preguntas_frecuentes=perfil["preguntas_frecuentes"],
        competidores=perfil["competidores"],
        marca={
            "logo_url": logo_url,
            "colores": colores,
            "bio_instagram": datos_ig.get("bio"),
            "seguidores": datos_ig.get("seguidores"),
            "descripcion_facebook": datos_fb.get("descripcion"),
            "tecnologias": ficha.tecnologias,
        },
    )

    supabase.guardar_negocio(ficha, resultado.analisis, es_cliente=True)
    return paquete

# ─── Flujo D: decisores B2B ──────────────────────────────────────────


def buscar_personas(
    rubro: str,
    ciudad: str | None = None,
    cargos: list[str] | None = None,
    cantidad: int = 20,
) -> list[Persona]:
    personas = linkedin.buscar_decisores(rubro, ciudad, cargos, cantidad)
    if personas:
        supabase.guardar_personas(personas)
        supabase.registrar_investigacion(
            "personas", {"rubro": rubro, "ciudad": ciudad}, len(personas)
        )
    return personas


# ─── Flujo E: cazador de recursos, créditos y beneficios ─────────────


def listar_recursos(filtro: FiltroRecursos) -> list[Recurso]:
    """Obtiene y filtra recursos del catálogo (créditos cloud, devs, .edu, B2B)."""
    return filtrar_recursos(filtro)


def cazar_recursos_web(
    termino: str = "creditos startups cloud 2026",
    pais: str | None = None,
    cantidad: int = 10,
) -> list[Recurso]:
    """Busca en vivo convocatorias abiertas y grants en la web."""
    return buscar_oportunidades_web(termino_busqueda=termino, pais_o_region=pais, cantidad=cantidad)


def generar_postulacion_recurso(peticion: PeticionPostulacion) -> RespuestaPostulacion:
    """Genera respuestas y pitch a medida para formularios de postulación."""
    return generar_postulacion(peticion)
