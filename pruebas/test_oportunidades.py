"""Prueba el motor de puntuación por reglas (el que corre sin IA)."""

from aplicacion.ia import _analisis_por_reglas


def test_sin_web_puntua_alto():
    analisis = _analisis_por_reglas(
        {"nombre": "Barbería X", "telefono": "+5491145678900", "cantidad_resenas": 150}
    )
    assert analisis.puntuacion >= 70
    assert any(o.tipo == "web" for o in analisis.oportunidades)


def test_negocio_ya_digitalizado_puntua_bajo():
    analisis = _analisis_por_reglas(
        {
            "nombre": "Negocio Moderno",
            "web": "https://moderno.com",
            "web_funciona": True,
            "web_es_vieja": False,
            "tiene_chatbot": True,
            "tiene_reservas_online": True,
            "telefono": "+5491145678900",
            "cantidad_resenas": 10,
        }
    )
    assert analisis.puntuacion <= 50


def test_sin_contacto_penaliza():
    con_contacto = _analisis_por_reglas({"nombre": "A", "telefono": "+5491145678900"})
    sin_contacto = _analisis_por_reglas({"nombre": "B"})
    assert sin_contacto.puntuacion < con_contacto.puntuacion


def test_puntuacion_dentro_de_rango():
    for datos in ({}, {"nombre": "X"}, {"nombre": "Y", "cantidad_resenas": 5000}):
        analisis = _analisis_por_reglas(datos)
        assert 0 <= analisis.puntuacion <= 100


def test_whatsapp_manual_es_oportunidad():
    analisis = _analisis_por_reglas(
        {"nombre": "Z", "whatsapp": "+5491145678900", "tiene_reservas_online": False}
    )
    assert any(o.tipo == "whatsapp" for o in analisis.oportunidades)
