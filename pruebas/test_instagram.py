from aplicacion.buscadores import instagram


def test_usuario_desde_url():
    assert instagram.usuario_desde_url("https://www.instagram.com/barberiax/") == "barberiax"
    assert instagram.usuario_desde_url("instagram.com/yas.beauty_") == "yas.beauty_"
    assert instagram.usuario_desde_url("https://instagram.com/p/ABC123") is None
    assert instagram.usuario_desde_url("https://facebook.com/algo") is None


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


def test_descarta_el_logo_generico_de_instagram():
    assert instagram.logo_de_perfil(
        "https://static.cdninstagram.com/rsrc.php/v4/yD/r/R0fBIMurK8v.png"
    ) is None
    logo_real = "https://instagram.fabc1-1.fna.fbcdn.net/v/t51/perfil.jpg"
    assert instagram.logo_de_perfil(logo_real) == logo_real


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
