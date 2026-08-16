"""Un negocio cuya única 'web' es un perfil ajeno NO tiene web propia.

Es el caso que más importa: si lo tratamos como 'ya tiene web moderna con
reservas', descartamos justo a los mejores prospectos.
"""

from aplicacion.buscadores import web
from aplicacion.ia import _analisis_por_reglas


def test_detecta_plataformas_de_terceros():
    assert web.es_plataforma("https://agendapro.com/site/ar/laguarida/2328")
    assert web.es_plataforma("https://calendly.com/concepto5")
    assert web.es_plataforma("https://linktr.ee/barberiax")
    assert web.es_plataforma("https://www.facebook.com/barberiax")


def test_no_marca_sitios_propios():
    assert not web.es_plataforma("https://www.buenosairesbarbershop.com/")
    assert not web.es_plataforma("https://barberiax.com.ar")
    assert not web.es_plataforma("")


def test_perfil_ajeno_puntua_como_sin_web():
    en_plataforma = _analisis_por_reglas(
        {
            "nombre": "La Guarida",
            "web": "https://agendapro.com/site/ar/laguarida/2328",
            "web_funciona": True,
            "web_es_plataforma": True,
            "tiene_reservas_online": True,
            "telefono": "+5491135820869",
            "cantidad_resenas": 48,
        }
    )
    sin_web = _analisis_por_reglas(
        {"nombre": "Otra", "telefono": "+5491135820869", "cantidad_resenas": 48}
    )

    assert en_plataforma.puntuacion == sin_web.puntuacion
    assert any(o.tipo == "web" for o in en_plataforma.oportunidades)


def test_web_propia_moderna_puntua_menos_que_perfil_ajeno():
    perfil_ajeno = _analisis_por_reglas(
        {
            "nombre": "A",
            "web": "https://agendapro.com/site/ar/a/1",
            "web_es_plataforma": True,
            "web_funciona": True,
            "telefono": "+5491100000000",
        }
    )
    web_propia = _analisis_por_reglas(
        {
            "nombre": "B",
            "web": "https://b.com",
            "web_es_plataforma": False,
            "web_funciona": True,
            "web_es_vieja": False,
            "tiene_chatbot": True,
            "telefono": "+5491100000000",
        }
    )
    assert perfil_ajeno.puntuacion > web_propia.puntuacion
