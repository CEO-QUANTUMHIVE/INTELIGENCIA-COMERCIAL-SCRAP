"""Prueba que investigar_cliente() arme el paquete completo para Fábrica de
Webs y Fábrica de Agentes: antes de este cambio, servicios/precios/horarios/
preguntas_frecuentes/competidores quedaban siempre vacíos y facebook_url se
descartaba silenciosamente.
"""

from aplicacion import coordinador


def test_investigar_cliente_arma_paquete_completo(monkeypatch):
    def _enriquecer_falso(negocio):
        negocio.texto_web = "Cortamos pelo. Corte $8000. Abrimos 9 a 19."
        negocio.logo_url = "https://barberiax.com/logo.png"
        return negocio

    monkeypatch.setattr(coordinador.enriquecedor, "enriquecer", _enriquecer_falso)
    monkeypatch.setattr(
        coordinador.instagram, "leer", lambda url: {"bio": "la mejor barbería", "seguidores": 500}
    )
    monkeypatch.setattr(
        coordinador.facebook, "leer", lambda url: {"descripcion": "barbería de barrio"}
    )
    monkeypatch.setattr(
        coordinador.perfil_cliente,
        "extraer",
        lambda datos: {
            "servicios": ["Corte"],
            "precios": ["Corte $8000"],
            "horarios": "9 a 19",
            "preguntas_frecuentes": [],
            "competidores": [],
        },
    )
    monkeypatch.setattr(
        coordinador.visual, "extraer_colores", lambda url, **k: ["#111111", "#eeeeee"]
    )
    monkeypatch.setattr(coordinador.supabase, "guardar_negocio", lambda *a, **k: "id-123")

    paquete = coordinador.investigar_cliente(
        nombre="Barbería X",
        web_url="https://barberiax.com",
        instagram_url="https://instagram.com/barberiax",
        facebook_url="https://facebook.com/barberiax",
    )

    assert paquete.servicios == ["Corte"]
    assert paquete.precios == ["Corte $8000"]
    assert paquete.horarios == "9 a 19"
    assert paquete.negocio.facebook == "https://facebook.com/barberiax"
    assert paquete.negocio.logo_url == "https://barberiax.com/logo.png"
    assert paquete.marca["bio_instagram"] == "la mejor barbería"
    assert paquete.marca["descripcion_facebook"] == "barbería de barrio"
    assert paquete.marca["logo_url"] == "https://barberiax.com/logo.png"
    assert paquete.marca["colores"] == ["#111111", "#eeeeee"]


def test_investigar_cliente_usa_logo_de_ig_si_la_web_no_tiene(monkeypatch):
    """Prioridad web > IG > FB: si la web no trae logo, cae al de Instagram."""

    monkeypatch.setattr(coordinador.enriquecedor, "enriquecer", lambda negocio: negocio)
    monkeypatch.setattr(
        coordinador.instagram,
        "leer",
        lambda url: {"bio": None, "logo_url": "https://instagram.com/x/foto.jpg"},
    )
    monkeypatch.setattr(coordinador.facebook, "leer", lambda url: {})
    monkeypatch.setattr(
        coordinador.perfil_cliente,
        "extraer",
        lambda datos: dict(coordinador.perfil_cliente.PERFIL_VACIO),
    )
    llamada = {}

    def _colores_falso(url, **kwargs):
        llamada["url"] = url
        return []

    monkeypatch.setattr(coordinador.visual, "extraer_colores", _colores_falso)
    monkeypatch.setattr(coordinador.supabase, "guardar_negocio", lambda *a, **k: None)

    paquete = coordinador.investigar_cliente(
        nombre="Kiosco Y", instagram_url="https://instagram.com/x"
    )

    assert paquete.marca["logo_url"] == "https://instagram.com/x/foto.jpg"
    assert llamada["url"] == "https://instagram.com/x/foto.jpg"


def test_investigar_cliente_no_revienta_sin_ia_ni_redes(monkeypatch):
    """Sin IA configurada y sin IG/FB, el paquete se arma igual, solo que
    con los campos de perfil vacíos (respaldo, no excepción)."""

    monkeypatch.setattr(coordinador.enriquecedor, "enriquecer", lambda negocio: negocio)
    monkeypatch.setattr(coordinador.supabase, "guardar_negocio", lambda *a, **k: None)

    paquete = coordinador.investigar_cliente(nombre="Kiosco Sin Redes")

    assert paquete.negocio.nombre == "Kiosco Sin Redes"
    assert paquete.servicios == []
    assert paquete.competidores == []
