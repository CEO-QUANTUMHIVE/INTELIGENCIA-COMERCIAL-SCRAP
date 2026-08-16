"""Limpia y normaliza los datos de contacto."""

import re

PREFIJOS_PAIS = {
    "argentina": "54",
    "chile": "56",
    "uruguay": "598",
    "mexico": "52",
    "españa": "34",
    "colombia": "57",
    "peru": "51",
}

PRIORIDAD_EMAIL = ("info@", "contacto@", "hola@", "ventas@", "consultas@", "administracion@")


def normalizar_telefono(telefono: str | None, pais: str = "argentina") -> str | None:
    """Deja el teléfono en formato internacional sin espacios ni símbolos."""
    if not telefono:
        return None

    solo_digitos = re.sub(r"[^\d+]", "", telefono)
    if not solo_digitos:
        return None

    if solo_digitos.startswith("+"):
        return solo_digitos

    prefijo = PREFIJOS_PAIS.get(pais.strip().lower(), "54")

    if solo_digitos.startswith("00"):
        return "+" + solo_digitos[2:]
    if solo_digitos.startswith(prefijo) and len(solo_digitos) > 10:
        return "+" + solo_digitos

    return "+" + prefijo + solo_digitos.lstrip("0")


def a_whatsapp(telefono: str | None) -> str | None:
    """Un móvil sirve como WhatsApp. Un fijo casi nunca."""
    normalizado = normalizar_telefono(telefono)
    if not normalizado:
        return None
    digitos = normalizado.lstrip("+")
    if len(digitos) < 10:
        return None
    return normalizado


def mejor_email(emails: list[str] | None) -> str | None:
    """Elige el email más útil de la lista."""
    if not emails:
        return None

    limpios = [e.strip().lower() for e in emails if "@" in e]
    if not limpios:
        return None

    for prefijo in PRIORIDAD_EMAIL:
        for email in limpios:
            if email.startswith(prefijo):
                return email

    # Los personales suelen ser mejores que los genéricos de plataforma
    no_genericos = [e for e in limpios if not e.startswith(("noreply", "no-reply", "postmaster"))]
    return (no_genericos or limpios)[0]


def hay_como_contactar(negocio) -> bool:
    return bool(
        getattr(negocio, "telefono", None)
        or getattr(negocio, "whatsapp", None)
        or getattr(negocio, "email", None)
        or getattr(negocio, "instagram", None)
    )
