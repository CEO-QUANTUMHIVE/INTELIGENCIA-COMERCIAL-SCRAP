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

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Scraping
NAVEGADOR_OCULTO = _bool("NAVEGADOR_OCULTO", True)
PAUSA_ENTRE_NEGOCIOS = float(os.getenv("PAUSA_ENTRE_NEGOCIOS", "1.5"))

# API
PUERTO = int(os.getenv("PUERTO", "8000"))
# Token que deben mandar los que consumen la API (Fábrica de Webs, Fábrica de
# Agentes, etc.) como "Authorization: Bearer <token>". Vacío = sin auth, para
# no trabar el desarrollo local; en producción hay que setearlo.
TOKEN_INTERNO = os.getenv("TOKEN_INTERNO", "")


def hay_supabase() -> bool:
    return bool(SUPABASE_URL and SUPABASE_KEY)


def hay_ia() -> bool:
    if PROVEEDOR_IA == "openai":
        return bool(OPENAI_API_KEY)
    return bool(ANTHROPIC_API_KEY)
