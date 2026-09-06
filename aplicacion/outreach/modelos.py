"""Contratos públicos del módulo de outreach."""

from typing import Literal

from pydantic import BaseModel


class ResultadoOutreach(BaseModel):
    negocio_id: str
    estado: Literal["enviado", "pendiente_manual", "pendiente_reintento"]
    canal: Literal["email", "instagram", "facebook", "whatsapp"]
    enviado: bool
    detalle: str
    contacto_id: int | None = None
    conversacion_id: int | None = None
    enlace_manual: str | None = None


class DecisionCanal(BaseModel):
    canal: Literal["email", "instagram", "facebook", "whatsapp"]
    automatico: bool
    inbox_id: int
    destino: str
    enlace_manual: str | None = None
