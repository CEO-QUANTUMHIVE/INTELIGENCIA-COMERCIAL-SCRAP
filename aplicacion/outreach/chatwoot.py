"""Cliente HTTP mínimo para la API autenticada de Chatwoot."""

import logging

import httpx

from aplicacion import configuracion
from aplicacion.modelos import Negocio

logger = logging.getLogger(__name__)


class ErrorChatwoot(RuntimeError):
    """La operación no pudo completarse después del reintento permitido."""


def _solicitar(metodo: str, ruta: str, **kwargs) -> dict:
    url = f"{configuracion.CHATWOOT_URL}{ruta}"
    headers = dict(kwargs.pop("headers", {}))
    headers["api_access_token"] = configuracion.CHATWOOT_API_KEY
    ultimo_error: Exception | None = None

    for intento in range(2):
        try:
            respuesta = httpx.request(
                metodo,
                url,
                headers=headers,
                timeout=configuracion.CHATWOOT_TIMEOUT,
                **kwargs,
            )
            if respuesta.status_code == 429 or respuesta.status_code >= 500:
                respuesta.raise_for_status()
            if respuesta.status_code >= 400:
                respuesta.raise_for_status()
            datos = respuesta.json()
            return datos if isinstance(datos, dict) else {"payload": datos}
        except (httpx.RequestError, httpx.HTTPStatusError) as error:
            ultimo_error = error
            reintentable = isinstance(error, httpx.RequestError)
            if isinstance(error, httpx.HTTPStatusError):
                reintentable = error.response.status_code == 429 or error.response.status_code >= 500
            if intento == 0 and reintentable:
                continue
            break

    raise ErrorChatwoot("Chatwoot no respondió correctamente") from ultimo_error


def _ruta(recurso: str) -> str:
    return f"/api/v1/accounts/{configuracion.CHATWOOT_ACCOUNT_ID}/{recurso.lstrip('/')}"


def _extraer_contacto(datos: dict) -> dict:
    payload = datos.get("payload")
    if isinstance(payload, list):
        return payload[0] if payload and isinstance(payload[0], dict) else {}
    if isinstance(payload, dict):
        return payload
    return datos if datos.get("id") else {}


def _fuente_para_inbox(contacto: dict, inbox_id: int) -> str | None:
    if contacto.get("source_id"):
        return str(contacto["source_id"])
    for enlace in contacto.get("contact_inboxes") or []:
        inbox = enlace.get("inbox") or {}
        if inbox.get("id") == inbox_id and enlace.get("source_id"):
            return str(enlace["source_id"])
    return None


def buscar_contacto(identificador: str) -> dict | None:
    datos = _solicitar("GET", _ruta("contacts/search"), params={"q": identificador})
    for contacto in datos.get("payload") or []:
        if contacto.get("identifier") == identificador:
            return contacto
    return None


def obtener_o_crear_contacto(
    negocio: Negocio,
    negocio_id: str,
    canal: str,
    inbox_id: int,
) -> tuple[int, str]:
    identificador = f"qh-outreach:{negocio_id}:{canal}:{inbox_id}"
    contacto = buscar_contacto(identificador)
    if contacto is None:
        datos = _solicitar(
            "POST",
            _ruta("contacts"),
            json={
                "inbox_id": inbox_id,
                "name": negocio.nombre,
                "email": negocio.email,
                "phone_number": negocio.whatsapp or negocio.telefono,
                "identifier": identificador,
                "additional_attributes": {
                    "empresa": negocio.nombre,
                    "canal_origen": canal,
                    "web": negocio.web,
                    "instagram": negocio.instagram,
                    "facebook": negocio.facebook,
                },
            },
        )
        contacto = _extraer_contacto(datos)

    contacto_id = contacto.get("id")
    fuente = _fuente_para_inbox(contacto, inbox_id)
    if not isinstance(contacto_id, int) or not fuente:
        raise ErrorChatwoot("Chatwoot no devolvió contacto y source_id válidos")
    return contacto_id, fuente


def buscar_conversacion(contacto_id: int, clave_outreach: str) -> dict | None:
    datos = _solicitar("GET", _ruta(f"contacts/{contacto_id}/conversations"))
    payload = datos.get("payload")
    conversaciones = payload if isinstance(payload, list) else datos.get("data") or []
    for conversacion in conversaciones:
        atributos = conversacion.get("custom_attributes") or {}
        if atributos.get("clave_outreach") == clave_outreach:
            return conversacion
    return None


def crear_conversacion(
    contacto_id: int,
    source_id: str,
    inbox_id: int,
    clave_outreach: str,
    negocio_id: str,
    canal: str,
) -> dict:
    return _solicitar(
        "POST",
        _ruta("conversations"),
        json={
            "source_id": source_id,
            "inbox_id": inbox_id,
            "contact_id": contacto_id,
            "status": "open",
            "custom_attributes": {
                "clave_outreach": clave_outreach,
                "negocio_id": negocio_id,
                "canal_outreach": canal,
            },
        },
    )


def conversacion_tiene_mensaje(conversacion_id: int, contenido: str, privado: bool) -> bool:
    datos = _solicitar("GET", _ruta(f"conversations/{conversacion_id}"))
    return any(
        mensaje.get("content") == contenido and bool(mensaje.get("private")) is privado
        for mensaje in datos.get("messages") or []
    )


def enviar_mensaje(conversacion_id: int, contenido: str, privado: bool) -> dict:
    return _solicitar(
        "POST",
        _ruta(f"conversations/{conversacion_id}/messages"),
        json={
            "content": contenido,
            "message_type": "outgoing",
            "private": privado,
            "content_type": "text",
        },
    )


def aplicar_etiqueta(conversacion_id: int, etiqueta: str) -> None:
    _solicitar(
        "POST",
        _ruta(f"conversations/{conversacion_id}/labels"),
        json={"labels": [etiqueta]},
    )
