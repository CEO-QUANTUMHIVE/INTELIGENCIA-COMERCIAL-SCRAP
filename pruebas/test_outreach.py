"""Pruebas del módulo 2: outreach auditable y sin DMs fríos simulados."""

import httpx
from fastapi.testclient import TestClient

from aplicacion import configuracion
from aplicacion.api import app
from aplicacion.modelos import Negocio
from aplicacion.outreach import chatwoot, servicio

cliente = TestClient(app)


def test_selecciona_email_automatico_primero(monkeypatch):
    monkeypatch.setattr(configuracion, "CHATWOOT_INBOX_EMAIL_ID", 12)
    monkeypatch.setattr(configuracion, "CHATWOOT_INBOX_MANUAL_ID", 34)
    negocio = Negocio(
        nombre="Demo",
        email="ventas@example.com",
        instagram="https://instagram.com/demo",
    )

    decision = servicio.seleccionar_canal(negocio, "Hola")

    assert decision.canal == "email"
    assert decision.automatico is True
    assert decision.inbox_id == 12


def test_instagram_frio_queda_manual(monkeypatch):
    monkeypatch.setattr(configuracion, "CHATWOOT_INBOX_EMAIL_ID", 0)
    monkeypatch.setattr(configuracion, "CHATWOOT_INBOX_MANUAL_ID", 34)
    negocio = Negocio(nombre="Demo", instagram="https://instagram.com/demo")

    decision = servicio.seleccionar_canal(negocio, "Hola")

    assert decision.canal == "instagram"
    assert decision.automatico is False
    assert decision.enlace_manual == "https://instagram.com/demo"


def test_whatsapp_manual_arma_link_al_prospecto(monkeypatch):
    monkeypatch.setattr(configuracion, "CHATWOOT_INBOX_EMAIL_ID", 0)
    monkeypatch.setattr(configuracion, "CHATWOOT_INBOX_MANUAL_ID", 34)
    negocio = Negocio(nombre="Demo", whatsapp="+54 9 11 4567-8900")

    decision = servicio.seleccionar_canal(negocio, "Hola, ¿cómo estás?")

    assert decision.canal == "whatsapp"
    assert decision.automatico is False
    assert decision.enlace_manual.startswith("https://wa.me/5491145678900?text=")
    assert "%C2%BF" in decision.enlace_manual


def test_cliente_chatwoot_reintenta_una_vez(monkeypatch):
    monkeypatch.setattr(configuracion, "CHATWOOT_URL", "https://chatwoot.example")
    monkeypatch.setattr(configuracion, "CHATWOOT_API_KEY", "secreto")
    monkeypatch.setattr(configuracion, "CHATWOOT_TIMEOUT", 2)
    llamadas = []

    def request(method, url, **kwargs):
        llamadas.append({"method": method, "url": url, **kwargs})
        peticion = httpx.Request(method, url)
        if len(llamadas) == 1:
            return httpx.Response(500, request=peticion, json={"error": "temporal"})
        return httpx.Response(200, request=peticion, json={"payload": []})

    monkeypatch.setattr(chatwoot.httpx, "request", request)

    assert chatwoot.buscar_contacto("qh:demo") is None
    assert len(llamadas) == 2
    assert llamadas[1]["headers"]["api_access_token"] == "secreto"


def _fila_negocio(**cambios):
    fila = {
        "id": "negocio-1",
        "nombre": "Negocio Demo",
        "email": "ventas@example.com",
        "mensaje_sugerido": "Hola, vi una oportunidad concreta para mejorar sus ventas.",
    }
    fila.update(cambios)
    return fila


def test_contactar_email_es_idempotente_si_mensaje_ya_existe(monkeypatch):
    monkeypatch.setattr(configuracion, "hay_chatwoot", lambda: True)
    monkeypatch.setattr(configuracion, "CHATWOOT_INBOX_EMAIL_ID", 12)
    monkeypatch.setattr(configuracion, "CHATWOOT_INBOX_MANUAL_ID", 34)
    monkeypatch.setattr(servicio.supabase, "obtener_negocio", lambda _: _fila_negocio())
    monkeypatch.setattr(
        servicio.chatwoot, "obtener_o_crear_contacto", lambda *_: (7, "source-7")
    )
    monkeypatch.setattr(
        servicio.chatwoot, "buscar_conversacion", lambda *_: {"id": 9}
    )
    monkeypatch.setattr(
        servicio.chatwoot, "conversacion_tiene_mensaje", lambda *_: True
    )
    monkeypatch.setattr(
        servicio.chatwoot,
        "enviar_mensaje",
        lambda *_: (_ for _ in ()).throw(AssertionError("no debe duplicar el mensaje")),
    )
    etiquetas = []
    monkeypatch.setattr(
        servicio.chatwoot, "aplicar_etiqueta", lambda conversacion, etiqueta: etiquetas.append((conversacion, etiqueta))
    )

    resultado = servicio.contactar("negocio-1")

    assert resultado.estado == "enviado"
    assert resultado.enviado is True
    assert resultado.conversacion_id == 9
    assert etiquetas == [(9, "outreach-email-enviado")]


def test_contactar_instagram_crea_nota_privada(monkeypatch):
    monkeypatch.setattr(configuracion, "hay_chatwoot", lambda: True)
    monkeypatch.setattr(configuracion, "CHATWOOT_INBOX_EMAIL_ID", 0)
    monkeypatch.setattr(configuracion, "CHATWOOT_INBOX_MANUAL_ID", 34)
    monkeypatch.setattr(
        servicio.supabase,
        "obtener_negocio",
        lambda _: _fila_negocio(email=None, instagram="https://instagram.com/demo"),
    )
    monkeypatch.setattr(
        servicio.chatwoot, "obtener_o_crear_contacto", lambda *_: (7, "source-7")
    )
    monkeypatch.setattr(servicio.chatwoot, "buscar_conversacion", lambda *_: None)
    monkeypatch.setattr(
        servicio.chatwoot, "crear_conversacion", lambda *_: {"id": 10}
    )
    monkeypatch.setattr(
        servicio.chatwoot, "conversacion_tiene_mensaje", lambda *_: False
    )
    enviados = []
    monkeypatch.setattr(
        servicio.chatwoot,
        "enviar_mensaje",
        lambda conversacion, contenido, privado: enviados.append((conversacion, contenido, privado)),
    )
    monkeypatch.setattr(servicio.chatwoot, "aplicar_etiqueta", lambda *_: None)

    resultado = servicio.contactar("negocio-1")

    assert resultado.estado == "pendiente_manual"
    assert resultado.enviado is False
    assert enviados[0][0] == 10
    assert "NO fue enviado" in enviados[0][1]
    assert enviados[0][2] is True


def test_falla_chatwoot_guarda_tarea_pendiente(monkeypatch):
    monkeypatch.setattr(configuracion, "hay_chatwoot", lambda: True)
    monkeypatch.setattr(configuracion, "CHATWOOT_INBOX_EMAIL_ID", 12)
    monkeypatch.setattr(configuracion, "CHATWOOT_INBOX_MANUAL_ID", 34)
    monkeypatch.setattr(servicio.supabase, "obtener_negocio", lambda _: _fila_negocio())
    monkeypatch.setattr(
        servicio.chatwoot,
        "obtener_o_crear_contacto",
        lambda *_: (_ for _ in ()).throw(chatwoot.ErrorChatwoot("caído")),
    )
    pendientes = []
    monkeypatch.setattr(
        servicio.supabase, "crear_tarea", lambda tipo, datos: pendientes.append((tipo, datos))
    )

    resultado = servicio.contactar("negocio-1")

    assert resultado.estado == "pendiente_reintento"
    assert resultado.enviado is False
    assert pendientes[0][0] == "outreach"


def test_endpoint_contactar_sigue_protegido(monkeypatch):
    monkeypatch.setattr(configuracion, "TOKEN_INTERNO", "privado")
    respuesta = cliente.post("/contactar/negocio-1")
    assert respuesta.status_code == 401


def test_endpoint_contactar_avisa_si_chatwoot_no_esta_configurado(monkeypatch):
    monkeypatch.setattr(configuracion, "TOKEN_INTERNO", "")
    monkeypatch.setattr(configuracion, "hay_chatwoot", lambda: False)
    respuesta = cliente.post("/contactar/negocio-1")
    assert respuesta.status_code == 503
    assert "no está configurado" in respuesta.json()["detail"]
