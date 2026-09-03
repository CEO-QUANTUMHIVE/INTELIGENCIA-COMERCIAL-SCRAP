"""Modelos de datos para el Cazador de Recursos, Créditos y Beneficios."""

from enum import Enum
from pydantic import BaseModel, Field


class TipoCorreoRequerido(str, Enum):
    ESTUDIANTE = "estudiante"      # Requiere correo universitario/institucional
    CORPORATIVO = "corporativo"    # Requiere correo con dominio propio (@miempresa.com)
    CUALQUIERA = "cualquiera"      # Sirve cualquier correo (Gmail, etc.)


class CategoriaRecurso(str, Enum):
    CLOUD = "cloud"                # Créditos AWS, GCP, Azure, Oracle, DigitalOcean
    AI_STARTUP = "ai_startup"      # NVIDIA Inception, OpenAI/Anthropic startups
    DEV_TOOLS = "dev_tools"        # GitHub, JetBrains, Cloudflare, MongoDB, Vercel
    EDUCATIVO = "educativo"        # Programas exclusivos para estudiantes verificados
    SAAS_PERKS = "saas_perks"      # HubSpot, Stripe, Notion, Figma, etc.
    SUBSIDIO = "subsidio"          # Fondos no reembolsables, grants estatales/privados


class Recurso(BaseModel):
    id: str
    nombre: str
    proveedor: str
    categoria: CategoriaRecurso
    beneficio_principal: str       # Ej: "$150,000 en créditos Azure + OpenAI tokens"
    monto_estimado_usd: float | None = None
    correo_requerido: TipoCorreoRequerido
    requisitos: list[str] = Field(default_factory=list)
    dificultad_aprobacion: str = "Media"  # "Baja" (Automático), "Media", "Alta" (Comité)
    tiempo_respuesta: str = "1-7 días"
    url_oficial: str
    descripcion: str
    instrucciones_postulacion: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class FiltroRecursos(BaseModel):
    categoria: CategoriaRecurso | None = None
    tiene_correo_estudiante: bool = False
    tiene_correo_corporativo: bool = False
    texto_busqueda: str | None = None


class PeticionPostulacion(BaseModel):
    recurso_id: str
    nombre_proyecto: str
    descripcion_proyecto: str
    tipo_postulante: str = "startup"  # "estudiante" o "startup" / "empresa"
    correo_a_usar: str
    url_proyecto: str | None = None
    stack_tecnologico: list[str] = Field(default_factory=list)


class RespuestaPostulacion(BaseModel):
    recurso_id: str
    nombre_recurso: str
    pitch_elevator: str
    caso_de_uso_creditos: str
    arquitectura_tecnica: str
    checklist_antes_de_enviar: list[str]
    url_postulacion: str
    generado_con_ia: bool = False
