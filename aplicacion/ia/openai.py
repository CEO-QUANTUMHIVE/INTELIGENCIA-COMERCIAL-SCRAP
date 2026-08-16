"""Análisis con OpenAI. Mismo contrato que claude.py."""

import json

from openai import OpenAI

from aplicacion import configuracion
from aplicacion.ia.esquema import ESQUEMA_ANALISIS, INSTRUCCIONES, armar_prompt

_cliente: OpenAI | None = None


def _obtener_cliente() -> OpenAI:
    global _cliente
    if _cliente is None:
        _cliente = OpenAI(api_key=configuracion.OPENAI_API_KEY)
    return _cliente


def analizar(datos_negocio: dict) -> dict:
    respuesta = _obtener_cliente().chat.completions.create(
        model=configuracion.MODELO_OPENAI,
        messages=[
            {"role": "system", "content": INSTRUCCIONES},
            {"role": "user", "content": armar_prompt(datos_negocio)},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "analisis_comercial",
                "schema": ESQUEMA_ANALISIS,
                "strict": True,
            },
        },
    )
    return json.loads(respuesta.choices[0].message.content)
