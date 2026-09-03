from aplicacion.buscadores import instagram


def test_usuario_desde_url():
    assert instagram.usuario_desde_url("https://www.instagram.com/barberiax/") == "barberiax"
    assert instagram.usuario_desde_url("instagram.com/yas.beauty_") == "yas.beauty_"
    assert instagram.usuario_desde_url("https://instagram.com/p/ABC123") is None
    assert instagram.usuario_desde_url("https://facebook.com/algo") is None


def test_normaliza_usuario_o_url():
    assert instagram.normalizar_url("@barberiax") == "https://www.instagram.com/barberiax/"
    assert instagram.normalizar_url("instagram.com/barberiax") == "https://www.instagram.com/barberiax/"


def test_numeros_con_separador_de_miles():
    assert instagram._a_numero("1,234") == 1234
    assert instagram._a_numero("1.234") == 1234
    assert instagram._a_numero("890") == 890


def test_numeros_abreviados():
    assert instagram._a_numero("1.2K") == 1200
    assert instagram._a_numero("3,5 M") == 3_500_000
    assert instagram._a_numero("12k") == 12_000


def test_numero_invalido():
    assert instagram._a_numero("") is None
    assert instagram._a_numero("muchos") is None


def test_extrae_seguidores_y_publicaciones():
    descripcion = "1,234 Followers, 567 Following, 89 Posts - See Instagram photos"
    encontrado = instagram.PATRON_NUMEROS.search(descripcion)
    assert encontrado
    assert instagram._a_numero(encontrado.group(1)) == 1234
    assert instagram._a_numero(encontrado.group(2)) == 89


def test_extrae_en_espanol():
    descripcion = "2.500 seguidores, 300 seguidos, 120 publicaciones"
    encontrado = instagram.PATRON_NUMEROS.search(descripcion)
    assert encontrado
    assert instagram._a_numero(encontrado.group(1)) == 2500
    assert instagram._a_numero(encontrado.group(2)) == 120


def test_apify_usa_bearer_y_normaliza_respuesta(monkeypatch):
    monkeypatch.setattr(instagram.configuracion, "APIFY_TOKEN", "token-secreto")
    monkeypatch.setattr(
        instagram.configuracion, "APIFY_INSTAGRAM_ACTOR", "apify~instagram-scraper"
    )
    monkeypatch.setattr(instagram.configuracion, "APIFY_INSTAGRAM_TIMEOUT", 12)
    llamada = {}

    class Respuesta:
        def raise_for_status(self):
            return None

        def json(self):
            return [
                {
                    "url": "https://www.instagram.com/barberiax",
                    "username": "barberiax",
                    "fullName": "Barbería X",
                    "biography": "Cortes y barba. Turnos por WhatsApp.",
                    "followersCount": 4500,
                    "postsCount": 120,
                    "profilePicUrlHD": "https://cdninstagram.com/foto.jpg",
                    "externalUrl": "https://barberiax.com",
                    "businessEmail": "hola@barberiax.com",
                    "businessCategoryName": "Barbería",
                }
            ]

    def post(url, **kwargs):
        llamada.update(url=url, **kwargs)
        return Respuesta()

    monkeypatch.setattr(instagram.httpx, "post", post)

    resultado = instagram.leer("@barberiax")

    assert llamada["url"].endswith(
        "/acts/apify~instagram-scraper/run-sync-get-dataset-items"
    )
    assert llamada["headers"] == {"Authorization": "Bearer token-secreto"}
    assert llamada["json"] == {
        "directUrls": ["https://www.instagram.com/barberiax/"],
        "resultsType": "details",
        "resultsLimit": 1,
    }
    assert "token-secreto" not in llamada["url"]
    assert resultado["bio"] == "Cortes y barba. Turnos por WhatsApp."
    assert resultado["seguidores"] == 4500
    assert resultado["publicaciones"] == 120
    assert resultado["logo_url"] == "https://cdninstagram.com/foto.jpg"
    assert resultado["fuente"] == "apify"
    assert resultado["activo"] is True


def test_apify_falla_y_degrada_al_lector_publico(monkeypatch):
    monkeypatch.setattr(instagram.configuracion, "APIFY_TOKEN", "token-secreto")
    monkeypatch.setattr(
        instagram.configuracion, "APIFY_INSTAGRAM_ACTOR", "apify~instagram-scraper"
    )
    monkeypatch.setattr(
        instagram.httpx,
        "post",
        lambda *a, **k: (_ for _ in ()).throw(instagram.httpx.TimeoutException("timeout")),
    )
    monkeypatch.setattr(
        instagram,
        "_leer_publico",
        lambda valor: {"instagram": instagram.normalizar_url(valor), "fuente": "respaldo"},
    )

    resultado = instagram.leer("barberiax")

    assert resultado["fuente"] == "respaldo"
