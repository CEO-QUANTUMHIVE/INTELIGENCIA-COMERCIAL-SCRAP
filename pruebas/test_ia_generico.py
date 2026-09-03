"""Prueba `analizar_con_esquema`, la primitiva de IA genérica que comparten
el scoring comercial, el perfil de cliente y (a futuro) capital.

Usa el proveedor openai para los mocks porque es el único de los dos SDKs
de IA instalado en este entorno de pruebas — el contrato es idéntico al
de claude.py (`analizar(datos, esquema, instrucciones, encabezado=None)`).
"""

from aplicacion import configuracion
from aplicacion.ia import analizar_con_esquema

ESQUEMA_DE_PRUEBA = {"type": "object", "properties": {}}


def test_sin_ia_configurada_devuelve_none(monkeypatch):
    monkeypatch.setattr(configuracion, "ANTHROPIC_API_KEY", "")
    monkeypatch.setattr(configuracion, "OPENAI_API_KEY", "")

    resultado = analizar_con_esquema({"a": 1}, ESQUEMA_DE_PRUEBA, "instrucciones")

    assert resultado is None


def test_marcador_de_env_no_cuenta_como_ia_configurada(monkeypatch):
    monkeypatch.setattr(configuracion, "PROVEEDOR_IA", "openai")
    monkeypatch.setattr(configuracion, "OPENAI_API_KEY", "tu_clave_openai_aqui")

    assert configuracion.hay_ia() is False


def test_marcadores_de_env_no_cuentan_como_supabase(monkeypatch):
    monkeypatch.setattr(configuracion, "SUPABASE_URL", "tu_url_de_supabase")
    monkeypatch.setattr(configuracion, "SUPABASE_KEY", "tu_clave_supabase_aqui")

    assert configuracion.hay_supabase() is False


def test_llama_al_proveedor_configurado_y_devuelve_su_resultado(monkeypatch):
    monkeypatch.setattr(configuracion, "OPENAI_API_KEY", "clave-de-prueba")
    monkeypatch.setattr(configuracion, "PROVEEDOR_IA", "openai")

    llamada = {}

    def _analizar_falso(datos, esquema, instrucciones, encabezado=None):
        llamada.update(
            datos=datos, esquema=esquema, instrucciones=instrucciones, encabezado=encabezado
        )
        return {"ok": True}

    import aplicacion.ia.openai as openai_proveedor

    monkeypatch.setattr(openai_proveedor, "analizar", _analizar_falso)

    resultado = analizar_con_esquema(
        {"a": 1}, ESQUEMA_DE_PRUEBA, "instrucciones", encabezado="Encabezado custom"
    )

    assert resultado == {"ok": True}
    assert llamada["datos"] == {"a": 1}
    assert llamada["esquema"] == ESQUEMA_DE_PRUEBA
    assert llamada["encabezado"] == "Encabezado custom"


def test_si_el_proveedor_revienta_devuelve_none(monkeypatch):
    monkeypatch.setattr(configuracion, "OPENAI_API_KEY", "clave-de-prueba")
    monkeypatch.setattr(configuracion, "PROVEEDOR_IA", "openai")

    def _revienta(*args, **kwargs):
        raise RuntimeError("la API está caída")

    import aplicacion.ia.openai as openai_proveedor

    monkeypatch.setattr(openai_proveedor, "analizar", _revienta)

    resultado = analizar_con_esquema({"a": 1}, ESQUEMA_DE_PRUEBA, "instrucciones")

    assert resultado is None
