"""Toda la configuración del sistema en un solo lugar."""

import os

from dotenv import load_dotenv

load_dotenv()


def _bool(nombre: str, por_defecto: bool) -> bool:
    valor = os.getenv(nombre)
    if valor is None:
        return por_defecto
    return valor.strip().lower() in ("1", "true", "si", "sí", "yes")


# IA
PROVEEDOR_IA = os.getenv("PROVEEDOR_IA", "claude").strip().lower()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODELO_CLAUDE = os.getenv("MODELO_CLAUDE", "claude-opus-5")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODELO_OPENAI = os.getenv("MODELO_OPENAI", "gpt-5")
# Para usar un proveedor compatible con la API de OpenAI (ej. Groq) en vez
# de OpenAI real: setear esto a su base_url y poner su API key en
# OPENAI_API_KEY. Vacío = OpenAI de verdad.
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "").strip() or None

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Scraping
NAVEGADOR_OCULTO = _bool("NAVEGADOR_OCULTO", True)
PAUSA_ENTRE_NEGOCIOS = float(os.getenv("PAUSA_ENTRE_NEGOCIOS", "1.5"))
APIFY_TOKEN = os.getenv("APIFY_TOKEN", "").strip()
APIFY_INSTAGRAM_ACTOR = os.getenv(
    "APIFY_INSTAGRAM_ACTOR", "apify~instagram-scraper"
).strip()
APIFY_INSTAGRAM_TIMEOUT = float(os.getenv("APIFY_INSTAGRAM_TIMEOUT", "120"))
APIFY_BUSQUEDA_ACTOR = os.getenv(
    "APIFY_BUSQUEDA_ACTOR", "apify~google-search-scraper"
).strip()
APIFY_BUSQUEDA_TIMEOUT = float(os.getenv("APIFY_BUSQUEDA_TIMEOUT", "120"))
APIFY_BUSQUEDA_MAX_COSTO_USD = float(
    os.getenv("APIFY_BUSQUEDA_MAX_COSTO_USD", "0.50")
)

# API
PUERTO = int(os.getenv("PUERTO", "8000"))
# Token que deben mandar los que consumen la API (Fábrica de Webs, Fábrica de
# Agentes, etc.) como "Authorization: Bearer <token>". Vacío = sin auth, para
# no trabar el desarrollo local; en producción hay que setearlo.
TOKEN_INTERNO = os.getenv("TOKEN_INTERNO", "")


def _tiene_valor_real(valor: str | None) -> bool:
    """Distingue una credencial real de los marcadores incluidos en `.env`.

    Los ejemplos permiten arrancar el proyecto, pero no deben hacer que `/salud`
    anuncie IA o Supabase como configurados ni provocar llamadas externas con
    claves del tipo ``tu_clave_aqui``.
    """
    if not valor or not valor.strip():
        return False

    normalizado = valor.strip().lower().replace("-", "_").replace(" ", "_")
    marcadores = (
        "tu_clave",
        "tu_url",
        "pega_",
        "aqui",
        "example",
        "ejemplo",
        "your_key",
        "your_url",
        "changeme",
    )
    return not any(marcador in normalizado for marcador in marcadores)


def hay_supabase() -> bool:
    return _tiene_valor_real(SUPABASE_URL) and _tiene_valor_real(SUPABASE_KEY)


def hay_ia() -> bool:
    if PROVEEDOR_IA == "openai":
        return _tiene_valor_real(OPENAI_API_KEY)
    return _tiene_valor_real(ANTHROPIC_API_KEY)


def hay_apify_instagram() -> bool:
    """Indica si el proveedor pago de Instagram puede usarse."""
    return _tiene_valor_real(APIFY_TOKEN) and bool(APIFY_INSTAGRAM_ACTOR)


def hay_apify_busqueda() -> bool:
    """Indica si el buscador web de recursos puede ejecutar su Actor."""
    return _tiene_valor_real(APIFY_TOKEN) and bool(APIFY_BUSQUEDA_ACTOR)
