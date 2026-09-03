"""Módulo Cazador de Recursos, Créditos Cloud, Developers y Beneficios Educativos."""

from aplicacion.recursos.catalogo import CATALOGO_RECURSOS, filtrar_recursos, obtener_recurso
from aplicacion.recursos.postulador import generar_postulacion
from aplicacion.recursos.cazador import buscar_oportunidades_web

__all__ = [
    "CATALOGO_RECURSOS",
    "filtrar_recursos",
    "obtener_recurso",
    "generar_postulacion",
    "buscar_oportunidades_web",
]
