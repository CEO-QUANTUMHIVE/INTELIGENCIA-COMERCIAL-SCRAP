"""Extrae el perfil de onboarding de un cliente: servicios, precios,
horarios, preguntas frecuentes y competidores — a partir de lo que ya
scrapeamos de su web e Instagram/Facebook.

Usa la misma primitiva genérica que el scoring comercial
(`aplicacion.ia.analizar_con_esquema`), con su propio esquema y prompt.
"""

import logging

from aplicacion.ia import analizar_con_esquema

logger = logging.getLogger(__name__)

PERFIL_VACIO = {
    "servicios": [],
    "precios": [],
    "horarios": None,
    "preguntas_frecuentes": [],
    "competidores": [],
}

ESQUEMA_PERFIL = {
    "type": "object",
    "properties": {
        "servicios": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Servicios o productos que ofrece, tal como figuran en el texto.",
        },
        "precios": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Precios mencionados literalmente (ej: 'Corte $8000'). Vacío si no hay.",
        },
        "horarios": {
            "type": ["string", "null"],
            "description": "Horario de atención si figura en el texto. null si no aparece.",
        },
        "preguntas_frecuentes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "pregunta": {"type": "string"},
                    "respuesta": {"type": "string"},
                },
                "required": ["pregunta", "respuesta"],
                "additionalProperties": False,
            },
            "description": "FAQ que ya esté publicada en la web. No inventar preguntas nuevas.",
        },
        "competidores": {
            "type": "array",
            "items": {"type": "string"},
            "description": (
                "Nombres de negocios competidores solo si aparecen mencionados "
                "explícitamente en el texto (reseñas, comparaciones, etc). Vacío si no hay."
            ),
        },
    },
    "required": ["servicios", "precios", "horarios", "preguntas_frecuentes", "competidores"],
    "additionalProperties": False,
}

INSTRUCCIONES = """Sos el encargado de onboarding de QuantumHive. Recibís lo que se pudo \
scrapear públicamente de un cliente que ya contrató (texto de su web, bio de Instagram, \
descripción de Facebook) y tenés que armar la ficha que van a usar la Fábrica de Webs y la \
Fábrica de Agentes para construirle su sitio y su agente de IA.

Reglas estrictas:
- Sacá SOLO lo que está explícito en el texto que te paso. No inventes servicios, precios, \
horarios ni preguntas frecuentes que no figuren.
- Si algo no aparece, dejalo vacío (lista vacía o null). Un campo vacío es mejor que un dato \
inventado: alguien va a usar esto para escribir la web real del cliente.
- Competidores: solo si el propio negocio los menciona o quedan claros por contraste directo \
en el texto. Si no hay señal clara, lista vacía. No completes con negocios genéricos del rubro."""


ENCABEZADO = "Armá la ficha de onboarding con estos datos públicos del cliente:"


def extraer(datos: dict) -> dict:
    """Devuelve el perfil extraído, o `PERFIL_VACIO` si no hay IA configurada
    o la extracción falla. Nunca revienta: el paquete se arma igual, solo que
    con esos campos vacíos para completar a mano.
    """
    resultado = analizar_con_esquema(datos, ESQUEMA_PERFIL, INSTRUCCIONES, ENCABEZADO)
    if resultado is None:
        logger.warning("Sin IA disponible: perfil de cliente queda con campos vacíos.")
        return dict(PERFIL_VACIO)
    return resultado
