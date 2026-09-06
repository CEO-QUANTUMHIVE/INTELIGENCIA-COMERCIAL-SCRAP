"""Decisión de canal y orquestación segura del primer contacto."""

import hashlib
import logging
import re
from urllib.parse import quote, urlparse

from aplicacion import configuracion
from aplicacion.base_datos import supabase
from aplicacion.modelos import Negocio
from aplicacion.outreach import chatwoot
from aplicacion.outreach.modelos import DecisionCanal, ResultadoOutreach

logger = logging.getLogger(__name__)


class NegocioNoEncontrado(LookupError):
    pass


class OutreachNoDisponible(RuntimeError):
    pass


class ProspectoNoContactable(ValueError):
    pass


def _enlace_whatsapp(numero: str, mensaje: str) -> str | None:
    digitos = re.sub(r"\D", "", numero or "")
    if len(digitos) < 8:
        return None
    return f"https://wa.me/{digitos}?text={quote(mensaje)}"


def _enlace_publico(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urlparse(url)
    return url if parsed.scheme in {"http", "https"} and parsed.netloc else None


def seleccionar_canal(negocio: Negocio, mensaje: str) -> DecisionCanal:
    """Prioriza email automático; las redes frías quedan como acción manual."""
    if negocio.email and configuracion.CHATWOOT_INBOX_EMAIL_ID > 0:
        return DecisionCanal(
            canal="email",
            automatico=True,
            inbox_id=configuracion.CHATWOOT_INBOX_EMAIL_ID,
            destino=negocio.email,
        )

    if configuracion.CHATWOOT_INBOX_MANUAL_ID > 0:
        if negocio.instagram and _enlace_publico(negocio.instagram):
            return DecisionCanal(
                canal="instagram",
                automatico=False,
                inbox_id=configuracion.CHATWOOT_INBOX_MANUAL_ID,
                destino=negocio.instagram,
                enlace_manual=negocio.instagram,
            )
        if negocio.facebook and _enlace_publico(negocio.facebook):
            return DecisionCanal(
                canal="facebook",
                automatico=False,
                inbox_id=configuracion.CHATWOOT_INBOX_MANUAL_ID,
                destino=negocio.facebook,
                enlace_manual=negocio.facebook,
            )
        numero = negocio.whatsapp or negocio.telefono
        enlace = _enlace_whatsapp(numero or "", mensaje)
        if numero and enlace:
            return DecisionCanal(
                canal="whatsapp",
                automatico=False,
                inbox_id=configuracion.CHATWOOT_INBOX_MANUAL_ID,
                destino=numero,
                enlace_manual=enlace,
            )

    raise ProspectoNoContactable("No hay un canal de contacto con inbox configurado")


def _nota_manual(decision: DecisionCanal, mensaje: str) -> str:
    return (
        "PENDIENTE DE CONTACTO MANUAL — este mensaje NO fue enviado.\n\n"
        f"Canal: {decision.canal}\n"
        f"Abrir: {decision.enlace_manual}\n\n"
        "Mensaje sugerido para revisar y copiar:\n"
        f"{mensaje}"
    )


def contactar(negocio_id: str) -> ResultadoOutreach:
    if not configuracion.hay_chatwoot():
        raise OutreachNoDisponible("Chatwoot todavía no está configurado")

    fila = supabase.obtener_negocio(negocio_id)
    if fila is None:
        raise NegocioNoEncontrado(negocio_id)

    mensaje = (fila.get("mensaje_sugerido") or "").strip()
    if not mensaje:
        raise ProspectoNoContactable("El negocio no tiene mensaje sugerido aprobado")

    negocio = Negocio(**fila)
    decision = seleccionar_canal(negocio, mensaje)
    clave = hashlib.sha256(
        f"{negocio_id}|{decision.canal}|{mensaje}".encode("utf-8")
    ).hexdigest()
    contenido = mensaje if decision.automatico else _nota_manual(decision, mensaje)
    privado = not decision.automatico

    try:
        contacto_id, source_id = chatwoot.obtener_o_crear_contacto(
            negocio, negocio_id, decision.canal, decision.inbox_id
        )
        conversacion = chatwoot.buscar_conversacion(contacto_id, clave)
        if conversacion is None:
            conversacion = chatwoot.crear_conversacion(
                contacto_id,
                source_id,
                decision.inbox_id,
                clave,
                negocio_id,
                decision.canal,
            )
        conversacion_id = conversacion.get("id")
        if not isinstance(conversacion_id, int):
            raise chatwoot.ErrorChatwoot("Chatwoot no devolvió una conversación válida")

        if not chatwoot.conversacion_tiene_mensaje(conversacion_id, contenido, privado):
            chatwoot.enviar_mensaje(conversacion_id, contenido, privado)

        etiqueta = (
            "outreach-email-enviado"
            if decision.automatico
            else f"{decision.canal}-pendiente-manual"
        )
        chatwoot.aplicar_etiqueta(conversacion_id, etiqueta)
        return ResultadoOutreach(
            negocio_id=negocio_id,
            estado="enviado" if decision.automatico else "pendiente_manual",
            canal=decision.canal,
            enviado=decision.automatico,
            detalle=(
                "Email enviado y conversación registrada en Chatwoot."
                if decision.automatico
                else "Nota privada creada en Chatwoot; requiere acción manual."
            ),
            contacto_id=contacto_id,
            conversacion_id=conversacion_id,
            enlace_manual=decision.enlace_manual,
        )
    except chatwoot.ErrorChatwoot as error:
        logger.error("Outreach pendiente para %s: %s", negocio_id, error)
        supabase.crear_tarea(
            "outreach",
            {"negocio_id": negocio_id, "canal": decision.canal, "motivo": "chatwoot_no_disponible"},
        )
        return ResultadoOutreach(
            negocio_id=negocio_id,
            estado="pendiente_reintento",
            canal=decision.canal,
            enviado=False,
            detalle="Chatwoot falló dos veces; el intento quedó pendiente para reproceso.",
            enlace_manual=decision.enlace_manual,
        )
