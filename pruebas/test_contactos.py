from aplicacion.enriquecimiento import contactos


def test_normaliza_telefono_argentino():
    assert contactos.normalizar_telefono("011 4567-8900") == "+541145678900"
    assert contactos.normalizar_telefono("+54 9 11 4567 8900") == "+5491145678900"
    assert contactos.normalizar_telefono("(11) 4567 8900") == "+541145678900"


def test_telefono_vacio():
    assert contactos.normalizar_telefono(None) is None
    assert contactos.normalizar_telefono("") is None
    assert contactos.normalizar_telefono("sin datos") is None


def test_prefijo_por_pais():
    assert contactos.normalizar_telefono("912345678", pais="chile").startswith("+56")


def test_whatsapp_descarta_numeros_cortos():
    assert contactos.a_whatsapp("1234") is None
    assert contactos.a_whatsapp("+54 9 11 4567 8900") == "+5491145678900"


def test_mejor_email_prioriza_los_utiles():
    emails = ["random@gmail.com", "info@negocio.com", "noreply@negocio.com"]
    assert contactos.mejor_email(emails) == "info@negocio.com"


def test_mejor_email_sin_genericos():
    assert contactos.mejor_email(["juan@negocio.com"]) == "juan@negocio.com"
    assert contactos.mejor_email([]) is None
    assert contactos.mejor_email(None) is None
