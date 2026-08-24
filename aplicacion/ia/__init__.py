"""Elige el proveedor de IA según la variable PROVEEDOR_IA.

Si no hay clave configurada, devuelve un análisis calculado con reglas simples
para que el sistema siga funcionando y puedas probar el scraping sin gastar.
"""

import logging

from aplicacion import configuracion
from aplicacion.modelos import Analisis

logger = logging.getLogger(__name__)


def analizar_con_esquema(
    datos: dict, esquema: dict, instrucciones: str, encabezado: str | None = None
) -> dict | None:
    """Primitiva genérica: le pide a la IA que devuelva `datos` moldeado a
    `esquema`. La usan tanto el scoring comercial como cualquier otra
    extracción estructurada (perfil de cliente, oportunidades de capital...).

    Devuelve None si no hay IA configurada o si falló — quien llama decide
    el respaldo (reglas, valores vacíos, lo que corresponda a ese caso).
    """
    if not configuracion.hay_ia():
        return None

    try:
        if configuracion.PROVEEDOR_IA == "openai":
            from aplicacion.ia import openai as proveedor
        else:
            from aplicacion.ia import claude as proveedor

        kwargs = {"encabezado": encabezado} if encabezado else {}
        return proveedor.analizar(datos, esquema, instrucciones, **kwargs)
    except Exception as error:  # noqa: BLE001
        logger.error("Falló la llamada a IA (%s).", error)
        return None


def analizar_negocio(datos_negocio: dict) -> Analisis:
    from aplicacion.ia.esquema import ESQUEMA_ANALISIS, INSTRUCCIONES

    resultado = analizar_con_esquema(datos_negocio, ESQUEMA_ANALISIS, INSTRUCCIONES)
    if resultado is None:
        logger.warning("Sin clave de IA o falló el análisis: uso puntuación por reglas.")
        return _analisis_por_reglas(datos_negocio)
    return Analisis(**resultado)


def _analisis_por_reglas(datos: dict) -> Analisis:
    """Respaldo sin IA. Sirve para probar el pipeline completo gratis."""
    puntos = 40
    problemas: list[str] = []
    oportunidades: list[dict] = []
    oferta: list[str] = []

    web = datos.get("web")
    if not web:
        puntos += 25
        problemas.append("No tiene sitio web.")
        oportunidades.append(
            {"tipo": "web", "motivo": "No existe presencia web propia.", "prioridad": "alta"}
        )
        oferta.append("Web inteligente QuantumHive")
    elif datos.get("web_es_plataforma"):
        # Su "web" es un perfil en Agendapro, Linktree, etc.: no tiene web propia.
        puntos += 25
        problemas.append("No tiene web propia: solo un perfil en una plataforma ajena.")
        oportunidades.append(
            {
                "tipo": "web",
                "motivo": "Depende de una plataforma de terceros en lugar de un sitio propio.",
                "prioridad": "alta",
            }
        )
        oferta.append("Web inteligente QuantumHive")
    elif datos.get("web_funciona") is False:
        puntos += 25
        problemas.append("La web no carga.")
        oportunidades.append(
            {"tipo": "web", "motivo": "El sitio está caído o roto.", "prioridad": "alta"}
        )
        oferta.append("Web inteligente QuantumHive")
    elif datos.get("web_es_vieja"):
        puntos += 15
        problemas.append("La web es vieja o no es responsive.")
        oportunidades.append(
            {"tipo": "web", "motivo": "Sitio desactualizado.", "prioridad": "media"}
        )
        oferta.append("Rediseño web")

    if not datos.get("tiene_chatbot"):
        puntos += 15
        problemas.append("No tiene atención automatizada.")
        oportunidades.append(
            {
                "tipo": "agente_ia",
                "motivo": "Sin chatbot ni agente de IA visible.",
                "prioridad": "alta",
            }
        )
        oferta.append("Agente de IA")

    if datos.get("whatsapp") and not datos.get("tiene_reservas_online"):
        puntos += 10
        problemas.append("Las reservas o consultas se manejan a mano por WhatsApp.")
        oportunidades.append(
            {
                "tipo": "whatsapp",
                "motivo": "WhatsApp sin automatizar.",
                "prioridad": "alta",
            }
        )
        oferta.append("Automatización de WhatsApp")

    resenas = datos.get("cantidad_resenas") or 0
    if resenas >= 100:
        puntos += 10
    elif resenas >= 30:
        puntos += 5

    if not (datos.get("telefono") or datos.get("whatsapp") or datos.get("email")):
        puntos -= 25
        problemas.append("No se encontró ningún canal de contacto.")

    puntos = max(0, min(100, puntos))
    nombre = datos.get("nombre", "el negocio")

    return Analisis(
        puntuacion=puntos,
        resumen=f"Análisis automático por reglas de {nombre}. Configurá una clave de IA para el análisis real.",
        problemas=problemas,
        oportunidades=oportunidades,
        oferta_recomendada=oferta,
        mensaje_sugerido="",
    )
