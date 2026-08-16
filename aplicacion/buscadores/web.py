"""Lee el sitio web de un negocio y saca todo lo útil.

Usa Scrapling: primero HTTP (rápido); si el sitio bloquea, navegador stealth.
"""

import logging
import re
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

PATRON_EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
PATRON_WHATSAPP = re.compile(r"(?:wa\.me/|api\.whatsapp\.com/send\?phone=)(\+?\d{6,15})")

EMAILS_BASURA = ("example.com", "sentry.io", "wixpress.com", "@2x", ".png", ".jpg")

SENALES_CHATBOT = (
    "tawk.to", "crisp.chat", "intercom", "drift.com", "zendesk", "tidio",
    "manychat", "botpress", "landbot", "chatwoot", "livechatinc", "smartsupp",
    "hubspot", "jivosite", "chatbot", "userlike", "whatsapp-widget",
)

SENALES_RESERVAS = (
    "calendly", "booksy", "fresha", "agendapro", "opentable", "mesa247",
    "simplybook", "setmore", "acuityscheduling", "reservar", "reservá",
    "turnos online", "sacar turno", "agendar cita", "book now", "meitre",
)

# Cuando el "sitio web" del negocio en realidad es su perfil en una plataforma
# ajena, no tiene web propia: es de los mejores prospectos que hay. Además, lo
# que se saque de esa página (Instagram, mails, tecnología) es de la plataforma,
# no del negocio, así que no lo tomamos.
PLATAFORMAS_TERCEROS = (
    "agendapro.com", "calendly.com", "booksy.com", "fresha.com",
    "linktr.ee", "linktree", "beacons.ai", "milink", "wa.me",
    "facebook.com", "instagram.com", "business.site", "negocio.site",
    "opentable.", "mesa247", "meitre.com", "simplybook", "setmore.com",
    "pedidosya", "rappi.com", "sites.google.com", "wixsite.com/blank",
)

TECNOLOGIAS = {
    "WordPress": ("wp-content", "wp-includes", "wordpress"),
    "Wix": ("wix.com", "wixstatic", "parastorage"),
    "Squarespace": ("squarespace",),
    "Shopify": ("cdn.shopify", "shopify"),
    "Webflow": ("webflow",),
    "Tiendanube": ("tiendanube", "nuvemshop"),
    "React/Next": ("_next/static", "__NEXT_DATA__"),
    "Elementor": ("elementor",),
}


def _traer(url: str):
    """Devuelve la página parseada o None."""
    from scrapling.fetchers import Fetcher, StealthyFetcher

    try:
        pagina = Fetcher.get(url, impersonate="chrome")
        if pagina is not None and pagina.status < 400:
            return pagina
        logger.info("HTTP %s en %s, reintento con navegador.", getattr(pagina, "status", "?"), url)
    except Exception as error:  # noqa: BLE001
        logger.info("Fetch HTTP falló en %s (%s), reintento con navegador.", url, error)

    try:
        return StealthyFetcher.fetch(url, headless=True)
    except Exception as error:  # noqa: BLE001
        logger.warning("No se pudo leer %s: %s", url, error)
        return None


def _enlaces(pagina) -> list[str]:
    salida = []
    for elemento in pagina.css("a"):
        href = elemento.attrib.get("href")
        if href:
            salida.append(href)
    return salida


def _fuentes_de_scripts(pagina) -> list[str]:
    salida = []
    for elemento in pagina.css("script"):
        src = elemento.attrib.get("src")
        if src:
            salida.append(src)
    return salida


def _normalizar(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        return "https://" + url
    return url


def leer(url: str) -> dict:
    """Devuelve todo lo que se pudo extraer del sitio."""
    url = _normalizar(url)
    resultado: dict = {
        "web": url,
        "es_plataforma": es_plataforma(url),
        "web_funciona": False,
        "web_es_vieja": None,
        "tiene_chatbot": False,
        "tiene_reservas_online": False,
        "tecnologias": [],
        "emails": [],
        "whatsapp": None,
        "instagram": None,
        "facebook": None,
        "linkedin": None,
        "texto_web": None,
    }

    pagina = _traer(url)
    if pagina is None:
        return resultado

    resultado["web_funciona"] = True

    if resultado["es_plataforma"]:
        # El negocio no tiene web propia: solo un perfil en una plataforma.
        # Sí sabemos que usa reservas online. Todo lo demás de esta página es
        # de la plataforma, así que no lo atribuimos al negocio.
        resultado["tiene_reservas_online"] = True
        return resultado

    texto = (pagina.get_all_text() or "")[:20000]
    enlaces = _enlaces(pagina)
    scripts = _fuentes_de_scripts(pagina)
    todo = " ".join([texto, " ".join(enlaces), " ".join(scripts)]).lower()

    resultado["texto_web"] = texto[:6000]

    # Contacto
    emails = {
        email.lower()
        for email in PATRON_EMAIL.findall(texto + " " + " ".join(enlaces))
        if not any(basura in email.lower() for basura in EMAILS_BASURA)
    }

    # Segunda pasada: página de contacto, ahí suele estar el mail bueno
    for enlace in enlaces:
        if re.search(r"contact|contacto", enlace, re.I):
            contacto = _traer(urljoin(url, enlace))
            if contacto is not None:
                texto_contacto = contacto.get_all_text() or ""
                emails |= {
                    email.lower()
                    for email in PATRON_EMAIL.findall(
                        texto_contacto + " " + " ".join(_enlaces(contacto))
                    )
                    if not any(b in email.lower() for b in EMAILS_BASURA)
                }
                todo += " " + texto_contacto.lower()
            break

    resultado["emails"] = sorted(emails)

    whatsapps = PATRON_WHATSAPP.findall(" ".join(enlaces))
    if whatsapps:
        resultado["whatsapp"] = whatsapps[0]

    for enlace in enlaces:
        bajo = enlace.lower()
        if "instagram.com/" in bajo and not resultado["instagram"]:
            resultado["instagram"] = enlace
        elif "facebook.com/" in bajo and not resultado["facebook"]:
            resultado["facebook"] = enlace
        elif "linkedin.com/" in bajo and not resultado["linkedin"]:
            resultado["linkedin"] = enlace

    # Señales
    resultado["tiene_chatbot"] = any(s in todo for s in SENALES_CHATBOT)
    resultado["tiene_reservas_online"] = any(s in todo for s in SENALES_RESERVAS)
    resultado["tecnologias"] = [
        nombre for nombre, marcas in TECNOLOGIAS.items() if any(m in todo for m in marcas)
    ]

    # ¿Web vieja? Sin viewport no es responsive: señal fuerte.
    sin_viewport = len(pagina.css('meta[name="viewport"]')) == 0
    usa_jquery_viejo = bool(re.search(r"jquery[/-]1\.\d", todo))
    resultado["web_es_vieja"] = bool(sin_viewport or usa_jquery_viejo)

    return resultado


def es_plataforma(url: str) -> bool:
    """¿La 'web' del negocio es en realidad su perfil en una plataforma ajena?"""
    if not url:
        return False
    return any(p in url.lower() for p in PLATAFORMAS_TERCEROS)


def dominio(url: str) -> str:
    try:
        return urlparse(_normalizar(url)).netloc.replace("www.", "")
    except Exception:  # noqa: BLE001
        return ""
