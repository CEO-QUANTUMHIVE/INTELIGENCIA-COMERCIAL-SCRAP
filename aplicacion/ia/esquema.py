"""El esquema JSON que la IA está obligada a devolver, y el prompt.

Vive aparte para que Claude y OpenAI usen exactamente el mismo contrato.
"""

TIPOS_OPORTUNIDAD = [
    "web",
    "agente_ia",
    "whatsapp",
    "reservas",
    "resenas",
    "redes",
    "automatizacion",
]

ESQUEMA_ANALISIS = {
    "type": "object",
    "properties": {
        "puntuacion": {
            "type": "integer",
            "description": "0 a 100. Qué tan buen prospecto es para QuantumHive.",
        },
        "resumen": {
            "type": "string",
            "description": "Dos o tres frases sobre el negocio y por qué contactarlo.",
        },
        "problemas": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Problemas concretos detectados en su presencia digital.",
        },
        "oportunidades": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "tipo": {"type": "string", "enum": TIPOS_OPORTUNIDAD},
                    "motivo": {"type": "string"},
                    "prioridad": {
                        "type": "string",
                        "enum": ["alta", "media", "baja"],
                    },
                },
                "required": ["tipo", "motivo", "prioridad"],
                "additionalProperties": False,
            },
        },
        "oferta_recomendada": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Qué productos de QuantumHive ofrecerle.",
        },
        "mensaje_sugerido": {
            "type": "string",
            "description": (
                "Primer mensaje de contacto, en español rioplatense, breve, "
                "personalizado con datos reales del negocio. Sin promesas vacías."
            ),
        },
    },
    "required": [
        "puntuacion",
        "resumen",
        "problemas",
        "oportunidades",
        "oferta_recomendada",
        "mensaje_sugerido",
    ],
    "additionalProperties": False,
}


INSTRUCCIONES = """Sos el analista comercial de QuantumHive, una empresa que vende:

- Webs inteligentes (rápidas, modernas, con IA integrada)
- Agentes de IA (atención al cliente, ventas, soporte, por WhatsApp/web/voz)
- Automatización de WhatsApp y reservas
- Empleados virtuales y avatares

Recibís los datos públicos de un negocio y tenés que decidir si es un buen \
prospecto y qué venderle.

Criterios de puntuación:
- Web inexistente, rota o vieja → oportunidad fuerte de web (+)
- `web_es_plataforma: true` significa que NO tiene web propia: lo que figura como \
web es su perfil en Agendapro, Linktree, Facebook o similar. Es de los mejores \
prospectos que hay, tratalo como "sin web" (+)
- Sin chatbot ni automatización visible → oportunidad de agente IA (+)
- Reservas o pedidos manuales por teléfono/WhatsApp → oportunidad de reservas (+)
- Muchas reseñas y buena reputación → tiene volumen y plata, mejor prospecto (+)
- Instagram activo pero web mala → desalineación, muy buen prospecto (+)
- Negocio ya digitalizado, con web moderna y chatbot → mal prospecto (-)
- Sin datos de contacto ni presencia → mal prospecto, no se puede llegar (-)

Sé honesto con la puntuación. Un 90 tiene que significar algo. Si el negocio no \
sirve, ponele 20 y decí por qué.

El mensaje sugerido tiene que mencionar algo concreto y verificable del negocio \
(su nombre, su rubro, algo que viste en su web o sus reseñas). Nada de plantillas \
genéricas. Máximo 4 líneas."""


def armar_prompt(datos_negocio: dict) -> str:
    import json

    return (
        "Analizá este negocio:\n\n"
        + json.dumps(datos_negocio, ensure_ascii=False, indent=2)
        + "\n\nDevolvé el análisis en el formato pedido."
    )
