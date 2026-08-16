"""Convierte un negocio enriquecido en una oportunidad comercial."""

import logging

from aplicacion.ia import analizar_negocio
from aplicacion.modelos import Analisis, Negocio

logger = logging.getLogger(__name__)

# Lo que le mandamos a la IA. El texto de la web va recortado: no hace falta
# más para decidir si el negocio sirve, y evita quemar tokens al pedo.
CAMPOS_PARA_IA = (
    "nombre", "categoria", "ciudad", "direccion", "telefono", "whatsapp",
    "email", "web", "instagram", "facebook", "puntuacion_google",
    "cantidad_resenas", "web_funciona", "web_es_vieja", "web_es_plataforma",
    "tiene_chatbot", "tiene_reservas_online", "tecnologias",
)


def analizar(negocio: Negocio) -> Analisis:
    datos = {campo: getattr(negocio, campo) for campo in CAMPOS_PARA_IA}
    if negocio.texto_web:
        datos["extracto_web"] = negocio.texto_web[:1500]
    return analizar_negocio(datos)


def analizar_lote(negocios: list[Negocio]) -> list[tuple[Negocio, Analisis]]:
    resultados = []
    for indice, negocio in enumerate(negocios, start=1):
        logger.info("Analizando [%s/%s] %s", indice, len(negocios), negocio.nombre)
        resultados.append((negocio, analizar(negocio)))
    return sorted(resultados, key=lambda par: par[1].puntuacion, reverse=True)
