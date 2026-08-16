from aplicacion.buscadores import web


def test_normaliza_urls():
    assert web._normalizar("negocio.com") == "https://negocio.com"
    assert web._normalizar("https://negocio.com") == "https://negocio.com"
    assert web._normalizar("http://negocio.com") == "http://negocio.com"


def test_dominio():
    assert web.dominio("https://www.barberiax.com/servicios") == "barberiax.com"
    assert web.dominio("barberiax.com") == "barberiax.com"


def test_patron_email_ignora_imagenes():
    texto = "escribinos a info@negocio.com o mira logo@2x.png"
    encontrados = web.PATRON_EMAIL.findall(texto)
    utiles = [e for e in encontrados if not any(b in e for b in web.EMAILS_BASURA)]
    assert utiles == ["info@negocio.com"]


def test_patron_whatsapp():
    enlaces = "https://wa.me/5491145678900 y https://api.whatsapp.com/send?phone=5491100000000"
    assert web.PATRON_WHATSAPP.findall(enlaces) == ["5491145678900", "5491100000000"]
