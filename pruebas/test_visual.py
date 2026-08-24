"""Prueba la extracción de colores dominantes de un logo/imagen de marca."""

import io

from aplicacion.enriquecimiento import visual


class _RespuestaFalsa:
    def __init__(self, content: bytes):
        self.content = content

    def raise_for_status(self) -> None:
        pass


def _png_solido(color: tuple[int, int, int]) -> bytes:
    from PIL import Image

    imagen = Image.new("RGB", (20, 20), color)
    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    return buffer.getvalue()


def test_sin_url_devuelve_lista_vacia():
    assert visual.extraer_colores(None) == []
    assert visual.extraer_colores("") == []


def test_imagen_de_un_solo_color_devuelve_ese_color(monkeypatch):
    contenido = _png_solido((255, 0, 0))

    import httpx

    monkeypatch.setattr(httpx, "get", lambda *a, **k: _RespuestaFalsa(contenido))

    colores = visual.extraer_colores("https://ejemplo.com/logo.png", cantidad=1)

    assert colores == ["#ff0000"]


def test_si_falla_la_descarga_devuelve_lista_vacia(monkeypatch):
    import httpx

    def _revienta(*args, **kwargs):
        raise httpx.ConnectError("no hay red")

    monkeypatch.setattr(httpx, "get", _revienta)

    assert visual.extraer_colores("https://ejemplo.com/logo.png") == []


def test_si_el_contenido_no_es_una_imagen_valida_devuelve_lista_vacia(monkeypatch):
    import httpx

    monkeypatch.setattr(httpx, "get", lambda *a, **k: _RespuestaFalsa(b"esto no es un png"))

    assert visual.extraer_colores("https://ejemplo.com/logo.png") == []
