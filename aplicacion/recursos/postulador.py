"""Generador asistido por IA para formularios de postulación a créditos y beneficios."""

import logging
from aplicacion.ia import analizar_con_esquema
from aplicacion.modelos_recursos import PeticionPostulacion, RespuestaPostulacion
from aplicacion.recursos.catalogo import obtener_recurso

logger = logging.getLogger(__name__)

ESQUEMA_POSTULACION = {
    "type": "object",
    "properties": {
        "pitch_elevator": {
            "type": "string",
            "description": "Pitch de 1 a 2 párrafos claro y contundente del proyecto, enfocado en impacto técnico e innovación.",
        },
        "caso_de_uso_creditos": {
            "type": "string",
            "description": "Explicación detallada de cómo se gastarán los créditos y por qué este proveedor es crítico para el éxito del proyecto.",
        },
        "arquitectura_tecnica": {
            "type": "string",
            "description": "Descripción de la arquitectura técnica mencionando servicios específicos del proveedor.",
        },
        "checklist_antes_de_enviar": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Lista de 3 a 5 puntos clave que el postulante debe verificar antes de enviar el formulario.",
        },
    },
    "required": [
        "pitch_elevator",
        "caso_de_uso_creditos",
        "arquitectura_tecnica",
        "checklist_antes_de_enviar",
    ],
    "additionalProperties": False,
}

PROMPT_POSTULACION = """Sos un asesor experto en postulaciones exitosas a programas de Startups, Créditos Cloud (AWS, Microsoft, Google Cloud, NVIDIA) y Beneficios de Developers/Educación.

Tu tarea es redactar las respuestas exactas que el postulante debe pegar en el formulario de aplicación para maximizar la probabilidad de aprobación al 100%.

Datos de la postulación:
- Programa / Recurso: {nombre_recurso} ({proveedor})
- Beneficio buscado: {beneficio}
- Tipo de postulante: {tipo_postulante}
- Correo a utilizar: {correo}
- Nombre del Proyecto: {nombre_proyecto}
- Descripción del Proyecto: {descripcion_proyecto}
- Stack Tecnológico: {stack}
- URL del Proyecto / Repositorio: {url_proyecto}

Instrucciones:
1. Usar un tono profesional, técnico, creíble y orientado a crecimiento.
2. Si el postulante es estudiante con correo .edu, enfatizar el uso educativo, de investigación, prototipado y aprendizaje de tecnologías avanzadas.
3. Si el postulante es startup con correo corporativo, enfatizar la escalabilidad, arquitectura cloud, retención de usuarios y el encaje con las tecnologías del proveedor.
4. Mapear explícitamente los servicios del proveedor con la arquitectura del proyecto (ej: si es Azure -> Azure App Services + Azure OpenAI; si es AWS -> ECS/Fargate + S3 + RDS).
5. Devolver SOLO el JSON con el esquema pedido.
"""


def _postulacion_por_defecto(peticion: PeticionPostulacion, nombre_recurso: str, url_postulacion: str) -> RespuestaPostulacion:
    """Generador basado en reglas cuando no hay IA configurada."""
    stack_str = ", ".join(peticion.stack_tecnologico) if peticion.stack_tecnologico else "Python, FastAPI, Docker, Cloud Services"

    if peticion.tipo_postulante == "estudiante":
        pitch = (
            f"{peticion.nombre_proyecto} es un proyecto académico y de desarrollo tecnológico enfocado en "
            f"{peticion.descripcion_proyecto}. El objetivo es implementar soluciones innovadoras aplicando "
            f"mejores prácticas de ingeniería de software."
        )
        caso_uso = (
            f"Utilizaremos los créditos y beneficios de {nombre_recurso} para desplegar entornos de prueba, "
            f"laboratorios de experimentación e integrar herramientas profesionales sin costos de infraestructura."
        )
        arquitectura = (
            f"Arquitectura modular construida sobre {stack_str}, utilizando microservicios conteinerizados "
            f"y APIs REST conectadas a bases de datos en la nube."
        )
        checklist = [
            f"Verificar que la cuenta esté registrada con tu correo de estudiante ({peticion.correo_a_usar}).",
            "Tener a mano comprobante de alumno regular o credencial estudiantil vigente.",
            "Asegurarse de que el repositorio de código o sitio web sea público si lo solicitan.",
        ]
    else:
        pitch = (
            f"{peticion.nombre_proyecto} es una solución tecnológica diseñada para {peticion.descripcion_proyecto}. "
            f"Nos encontramos en etapa de desarrollo y despliegue activo, buscando escalar nuestra infraestructura "
            f"y optimizar tiempos de respuesta para nuestros usuarios."
        )
        caso_uso = (
            f"Los créditos de {nombre_recurso} serán destinados al cómputo de producción, almacenamiento de datos, "
            f"consumo de APIs de modelos de lenguaje y aceleración de nuestros pipelines de CI/CD."
        )
        arquitectura = (
            f"Stack moderno basado en {stack_str}, con arquitectura desacoplada, alta disponibilidad "
            f"y despliegue automatizado en la nube del proveedor."
        )
        checklist = [
            f"Enviar la postulación utilizando el correo de dominio propio ({peticion.correo_a_usar}).",
            "Verificar que la web del proyecto esté online con HTTPS y enlaces funcionales.",
            "Tener el perfil de LinkedIn de la empresa y fundadores actualizado.",
        ]

    return RespuestaPostulacion(
        recurso_id=peticion.recurso_id,
        nombre_recurso=nombre_recurso,
        pitch_elevator=pitch,
        caso_de_uso_creditos=caso_uso,
        arquitectura_tecnica=arquitectura,
        checklist_antes_de_enviar=checklist,
        url_postulacion=url_postulacion,
        generado_con_ia=False,
    )


def generar_postulacion(peticion: PeticionPostulacion) -> RespuestaPostulacion:
    """Genera el contenido y argumentos para postular a un recurso."""
    recurso = obtener_recurso(peticion.recurso_id)
    nombre_recurso = recurso.nombre if recurso else peticion.recurso_id
    url_postulacion = recurso.url_oficial if recurso else "https://google.com"
    beneficio = recurso.beneficio_principal if recurso else "Créditos y licencias de software"
    proveedor = recurso.proveedor if recurso else "Proveedor Cloud/Dev"

    prompt = PROMPT_POSTULACION.format(
        nombre_recurso=nombre_recurso,
        proveedor=proveedor,
        beneficio=beneficio,
        tipo_postulante=peticion.tipo_postulante,
        correo=peticion.correo_a_usar,
        nombre_proyecto=peticion.nombre_proyecto,
        descripcion_proyecto=peticion.descripcion_proyecto,
        stack=", ".join(peticion.stack_tecnologico) if peticion.stack_tecnologico else "Python, FastAPI, IA, Docker",
        url_proyecto=peticion.url_proyecto or "En desarrollo local",
    )

    datos_proyecto = {
        "nombre_proyecto": peticion.nombre_proyecto,
        "descripcion_proyecto": peticion.descripcion_proyecto,
        "tipo_postulante": peticion.tipo_postulante,
        "correo": peticion.correo_a_usar,
        "stack": ", ".join(peticion.stack_tecnologico) if peticion.stack_tecnologico else "Python, FastAPI, IA, Docker",
        "url_proyecto": peticion.url_proyecto or "En desarrollo local",
        "programa": nombre_recurso,
        "proveedor": proveedor,
        "beneficio": beneficio,
    }

    try:
        resultado = analizar_con_esquema(datos_proyecto, ESQUEMA_POSTULACION, prompt)
        if resultado is None:
            return _postulacion_por_defecto(peticion, nombre_recurso, url_postulacion)
        return RespuestaPostulacion(
            recurso_id=peticion.recurso_id,
            nombre_recurso=nombre_recurso,
            pitch_elevator=resultado.get("pitch_elevator", ""),
            caso_de_uso_creditos=resultado.get("caso_de_uso_creditos", ""),
            arquitectura_tecnica=resultado.get("arquitectura_tecnica", ""),
            checklist_antes_de_enviar=resultado.get("checklist_antes_de_enviar", []),
            url_postulacion=url_postulacion,
            generado_con_ia=True,
        )
    except Exception as error:  # noqa: BLE001
        logger.warning("Fallo al generar postulación con IA, usando generador base: %s", error)
        return _postulacion_por_defecto(peticion, nombre_recurso, url_postulacion)
