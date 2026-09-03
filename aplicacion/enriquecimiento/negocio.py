"""Toma un negocio con datos básicos y le agrega todo lo que falta."""

import logging

from aplicacion.buscadores import facebook, instagram, web
from aplicacion.enriquecimiento import contactos
from aplicacion.modelos import Negocio

logger = logging.getLogger(__name__)


def enriquecer(negocio: Negocio) -> Negocio:
    """Visita la web y las redes del negocio y completa los campos vacíos."""

    if negocio.web:
        datos_web = web.leer(negocio.web)
        negocio.web_funciona = datos_web["web_funciona"]
        negocio.web_es_plataforma = datos_web["es_plataforma"]
        negocio.web_es_vieja = datos_web["web_es_vieja"]
        negocio.tiene_chatbot = datos_web["tiene_chatbot"]
        negocio.tiene_reservas_online = datos_web["tiene_reservas_online"]
        negocio.tecnologias = datos_web["tecnologias"]
        negocio.texto_web = datos_web["texto_web"]

        # De un perfil ajeno no se sacan contactos: son de la plataforma.
        if not datos_web["es_plataforma"]:
            negocio.email = negocio.email or contactos.mejor_email(datos_web["emails"])
            negocio.instagram = negocio.instagram or datos_web["instagram"]
            negocio.facebook = negocio.facebook or datos_web["facebook"]
            negocio.linkedin = negocio.linkedin or datos_web["linkedin"]
            negocio.logo_url = datos_web.get("logo_url")
            if datos_web["whatsapp"]:
                negocio.whatsapp = contactos.normalizar_telefono(datos_web["whatsapp"])
    else:
        negocio.web_funciona = False
        negocio.web_es_plataforma = False

    negocio.telefono = contactos.normalizar_telefono(negocio.telefono)
    negocio.whatsapp = negocio.whatsapp or contactos.a_whatsapp(negocio.telefono)

    if negocio.instagram:
        # Acá solo necesitamos canonizar la URL. La lectura completa se hace una
        # vez en investigar_cliente(), para no facturar dos consultas de Apify.
        negocio.instagram = instagram.normalizar_url(negocio.instagram)

    return negocio


def enriquecer_lote(negocios: list[Negocio]) -> list[Negocio]:
    salida = []
    for indice, negocio in enumerate(negocios, start=1):
        logger.info("Enriqueciendo [%s/%s] %s", indice, len(negocios), negocio.nombre)
        try:
            salida.append(enriquecer(negocio))
        except Exception as error:  # noqa: BLE001
            logger.error("Falló el enriquecimiento de %s: %s", negocio.nombre, error)
            salida.append(negocio)
    return salida


def leer_redes_sueltas(negocio: Negocio) -> Negocio:
    """Para cuando solo tenemos el Facebook o el Instagram y nada más."""
    if negocio.facebook and not negocio.nombre:
        datos_fb = facebook.leer(negocio.facebook)
        negocio.nombre = datos_fb["nombre"] or negocio.nombre
    return negocio
