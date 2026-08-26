"""Análisis con OpenAI. Mismo contrato que claude.py."""

import json

from openai import OpenAI

from aplicacion import configuracion
from aplicacion.ia.esquema import armar_prompt

_cliente: OpenAI | None = None


def _obtener_cliente() -> OpenAI:
    global _cliente
    if _cliente is None:
        _cliente = OpenAI(api_key=configuracion.OPENAI_API_KEY, base_url=configuracion.OPENAI_BASE_URL)
    return _cliente


def analizar(datos: dict, esquema: dict, instrucciones: str, encabezado: str | None = None) -> dict:
    contenido = armar_prompt(datos, encabezado) if encabezado else armar_prompt(datos)
    respuesta = _obtener_cliente().chat.completions.create(
        model=configuracion.MODELO_OPENAI,
        messages=[
            {"role": "system", "content": instrucciones},
            {"role": "user", "content": contenido},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "extraccion_estructurada",
                "schema": esquema,
                "strict": True,
            },
        },
    )
    return json.loads(respuesta.choices[0].message.content)
