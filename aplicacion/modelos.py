"""Las formas de los datos. Nada más que esto."""

from typing import Literal

from pydantic import BaseModel, Field


class Negocio(BaseModel):
    nombre: str
    categoria: str | None = None
    direccion: str | None = None
    ciudad: str | None = None
    telefono: str | None = None
    whatsapp: str | None = None
    email: str | None = None
    web: str | None = None
    instagram: str | None = None
    facebook: str | None = None
    linkedin: str | None = None
    puntuacion_google: float | None = None
    cantidad_resenas: int | None = None
    url_maps: str | None = None
    latitud: float | None = None
    longitud: float | None = None
    # Lo que detecta el enriquecimiento web
    web_funciona: bool | None = None
    web_es_vieja: bool | None = None
    # True cuando la "web" es solo un perfil en Agendapro, Linktree, etc.
    # Significa que el negocio NO tiene web propia.
    web_es_plataforma: bool | None = None
    tiene_chatbot: bool | None = None
    tiene_reservas_online: bool | None = None
    tecnologias: list[str] = Field(default_factory=list)
    texto_web: str | None = None
    # Logo o foto de perfil pública (og:image de la web, o si no hay, de IG/FB).
    # Es una URL externa: no se descarga ni se re-hostea acá.
    logo_url: str | None = None


class Oportunidad(BaseModel):
    tipo: Literal[
        "web",
        "agente_ia",
        "whatsapp",
        "reservas",
        "resenas",
        "redes",
        "automatizacion",
    ]
    motivo: str
    prioridad: Literal["alta", "media", "baja"] = "media"


class Analisis(BaseModel):
    """Lo que devuelve la IA para cada negocio."""

    puntuacion: int = Field(ge=0, le=100)
    resumen: str
    problemas: list[str] = Field(default_factory=list)
    oportunidades: list[Oportunidad] = Field(default_factory=list)
    oferta_recomendada: list[str] = Field(default_factory=list)
    mensaje_sugerido: str = ""


class NegocioAnalizado(BaseModel):
    negocio: Negocio
    analisis: Analisis | None = None


class Persona(BaseModel):
    """Decisor B2B (LinkedIn)."""

    nombre: str
    cargo: str | None = None
    empresa: str | None = None
    linkedin: str | None = None
    ciudad: str | None = None
    email: str | None = None


class PaquetePerfilCliente(BaseModel):
    """Lo que consumen la Fábrica de Webs y la Fábrica de Agentes."""

    negocio: Negocio
    servicios: list[str] = Field(default_factory=list)
    precios: list[str] = Field(default_factory=list)
    horarios: str | None = None
    preguntas_frecuentes: list[dict] = Field(default_factory=list)
    marca: dict = Field(default_factory=dict)
    competidores: list[str] = Field(default_factory=list)


# ─── Cuerpos de las peticiones a la API ──────────────────────────────


class PeticionBuscar(BaseModel):
    rubro: str = Field(description="Ej: barberías")
    ciudad: str = Field(description="Ej: Buenos Aires")
    cantidad: int = Field(default=20, ge=1, le=200)
    analizar: bool = True
    guardar: bool = True


class PeticionInvestigar(BaseModel):
    nombre: str | None = None
    web: str | None = None
    instagram: str | None = None
    facebook: str | None = None
    url_maps: str | None = None
    guardar: bool = True


class PeticionPersonas(BaseModel):
    rubro: str
    ciudad: str | None = None
    cargos: list[str] = Field(default_factory=lambda: ["CEO", "dueño", "director"])
    cantidad: int = Field(default=20, ge=1, le=100)
