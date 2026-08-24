"""Prueba la extracción de perfil de cliente (servicios, precios, horarios,
FAQ, competidores) para el paquete que consumen Fábrica de Webs y Agentes.
"""

from aplicacion import configuracion
from aplicacion.ia import perfil_cliente


def test_sin_ia_devuelve_perfil_vacio_sin_reventar(monkeypatch):
    monkeypatch.setattr(configuracion, "ANTHROPIC_API_KEY", "")
    monkeypatch.setattr(configuracion, "OPENAI_API_KEY", "")

    resultado = perfil_cliente.extraer({"nombre": "Barbería X", "texto_web": None})

    assert resultado == perfil_cliente.PERFIL_VACIO
    # Que sea una copia, no el mismo objeto: así nadie muta el default global.
    assert resultado is not perfil_cliente.PERFIL_VACIO


def test_con_ia_devuelve_lo_que_extrajo_el_proveedor(monkeypatch):
    extraido = {
        "servicios": ["Corte", "Barba"],
        "precios": ["Corte $8000"],
        "horarios": "Lun a sáb 9 a 19",
        "preguntas_frecuentes": [{"pregunta": "¿Hay estacionamiento?", "respuesta": "No"}],
        "competidores": [],
    }

    def _analizar_falso(datos, esquema, instrucciones, encabezado=None):
        assert esquema == perfil_cliente.ESQUEMA_PERFIL
        assert encabezado == perfil_cliente.ENCABEZADO
        return extraido

    # Se patchea la primitiva genérica (el seam real que usa perfil_cliente),
    # sin necesitar el paquete `anthropic` instalado para este test unitario.
    monkeypatch.setattr(perfil_cliente, "analizar_con_esquema", _analizar_falso)

    resultado = perfil_cliente.extraer({"nombre": "Barbería X"})

    assert resultado == extraido


def test_si_analizar_con_esquema_devuelve_none_cae_a_perfil_vacio(monkeypatch):
    # analizar_con_esquema devuelve None cuando la IA falló o no está
    # configurada (ver test_ia_generico.py) — extraer() tiene que degradar
    # con gracia, no reventar ni inventar datos.
    monkeypatch.setattr(perfil_cliente, "analizar_con_esquema", lambda *a, **k: None)

    resultado = perfil_cliente.extraer({"nombre": "Barbería X"})

    assert resultado == perfil_cliente.PERFIL_VACIO
