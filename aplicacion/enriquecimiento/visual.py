"""Saca los colores dominantes de una imagen pública (logo, foto de perfil).

Solo lee la imagen que ya se encontró por otro lado (og:image de la web, o
de Instagram/Facebook si la web no tenía) — nunca busca ni genera nada.
Mismo principio que el resto del enriquecimiento: si algo falla, devuelve
vacío, nunca revienta el paquete completo por esto.
"""

import logging

logger = logging.getLogger(__name__)

TAMANO_MUESTRA = (150, 150)
TIEMPO_ESPERA = 10


def extraer_colores(url_imagen: str | None, cantidad: int = 4) -> list[str]:
    """Devuelve hasta `cantidad` colores dominantes de la imagen, en hex,
    ordenados de más a menos presente. Lista vacía si no hay imagen o no se
    pudo descargar/procesar.
    """
    if not url_imagen:
        return []

    try:
        import io

        import httpx
        from PIL import Image

        respuesta = httpx.get(url_imagen, timeout=TIEMPO_ESPERA, follow_redirects=True)
        respuesta.raise_for_status()

        imagen = Image.open(io.BytesIO(respuesta.content)).convert("RGB")
        imagen.thumbnail(TAMANO_MUESTRA)

        paleta = imagen.quantize(colors=cantidad)
        colores_rgb = paleta.getpalette()
        conteo = sorted(paleta.getcolors(), reverse=True)

        hexadecimales = []
        for _cantidad, indice in conteo[:cantidad]:
            r, g, b = colores_rgb[indice * 3 : indice * 3 + 3]
            hexadecimales.append(f"#{r:02x}{g:02x}{b:02x}")
        return hexadecimales
    except Exception as error:  # noqa: BLE001
        logger.warning("No se pudieron sacar colores de %s: %s", url_imagen, error)
        return []
