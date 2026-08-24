"""Análisis con Claude (Anthropic). Mismo contrato que openai.py."""

import json

import anthropic

from aplicacion import configuracion
from aplicacion.ia.esquema import armar_prompt

_cliente: anthropic.Anthropic | None = None


def _obtener_cliente() -> anthropic.Anthropic:
    global _cliente
    if _cliente is None:
        _cliente = anthropic.Anthropic(api_key=configuracion.ANTHROPIC_API_KEY)
    return _cliente


def analizar(datos: dict, esquema: dict, instrucciones: str, encabezado: str | None = None) -> dict:
    contenido = armar_prompt(datos, encabezado) if encabezado else armar_prompt(datos)
    respuesta = _obtener_cliente().messages.create(
        model=configuracion.MODELO_CLAUDE,
        max_tokens=4000,
        system=instrucciones,
        output_config={
            "effort": "low",
            "format": {"type": "json_schema", "schema": esquema},
        },
        messages=[{"role": "user", "content": contenido}],
    )

    if respuesta.stop_reason == "refusal":
        raise RuntimeError("Claude rechazó la petición de análisis.")

    texto = next(b.text for b in respuesta.content if b.type == "text")
    return json.loads(texto)
