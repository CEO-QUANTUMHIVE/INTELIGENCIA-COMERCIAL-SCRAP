"""Outreach auditable mediante Chatwoot."""

from aplicacion.outreach.modelos import ResultadoOutreach
from aplicacion.outreach.servicio import contactar, seleccionar_canal

__all__ = ["ResultadoOutreach", "contactar", "seleccionar_canal"]
