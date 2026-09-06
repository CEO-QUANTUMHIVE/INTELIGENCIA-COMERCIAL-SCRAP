"""Todo lo que toca Supabase pasa por acá.

Si no hay credenciales configuradas, las funciones no explotan: avisan y
devuelven None. Así se puede probar el scraping antes de tener la base.
"""

import logging
from typing import Any

from aplicacion import configuracion
from aplicacion.modelos import Analisis, Negocio, Persona

logger = logging.getLogger(__name__)

_cliente = None


def cliente():
    global _cliente
    if not configuracion.hay_supabase():
        return None
    if _cliente is None:
        from supabase import create_client

        _cliente = create_client(configuracion.SUPABASE_URL, configuracion.SUPABASE_KEY)
    return _cliente


def _clave(negocio: Negocio) -> str:
    return negocio.url_maps or negocio.web or f"{negocio.nombre}|{negocio.ciudad or ''}"


def guardar_negocio(
    negocio: Negocio,
    analisis: Analisis | None = None,
    es_cliente: bool = False,
) -> str | None:
    """Inserta o actualiza el negocio. Devuelve su id."""
    supabase = cliente()
    if supabase is None:
        logger.warning("Sin Supabase configurado: no guardo %s", negocio.nombre)
        return None

    fila: dict[str, Any] = {
        "clave": _clave(negocio),
        "es_cliente": es_cliente,
        "nombre": negocio.nombre,
        "categoria": negocio.categoria,
        "direccion": negocio.direccion,
        "ciudad": negocio.ciudad,
        "telefono": negocio.telefono,
        "whatsapp": negocio.whatsapp,
        "email": negocio.email,
        "web": negocio.web,
        "instagram": negocio.instagram,
        "facebook": negocio.facebook,
        "linkedin": negocio.linkedin,
        "puntuacion_google": negocio.puntuacion_google,
        "cantidad_resenas": negocio.cantidad_resenas,
        "url_maps": negocio.url_maps,
        "latitud": negocio.latitud,
        "longitud": negocio.longitud,
        "web_funciona": negocio.web_funciona,
        "web_es_vieja": negocio.web_es_vieja,
        "web_es_plataforma": negocio.web_es_plataforma,
        "tiene_chatbot": negocio.tiene_chatbot,
        "tiene_reservas_online": negocio.tiene_reservas_online,
        "tecnologias": negocio.tecnologias,
    }

    if analisis:
        fila["puntuacion"] = analisis.puntuacion
        fila["resumen"] = analisis.resumen
        fila["mensaje_sugerido"] = analisis.mensaje_sugerido
        fila["datos"] = {
            "problemas": analisis.problemas,
            "oferta_recomendada": analisis.oferta_recomendada,
        }

    respuesta = (
        supabase.table("negocios")
        .upsert(fila, on_conflict="tenant_id,clave")
        .execute()
    )
    if not respuesta.data:
        return None

    negocio_id = respuesta.data[0]["id"]

    if analisis and analisis.oportunidades:
        supabase.table("oportunidades").delete().eq("negocio_id", negocio_id).execute()
        supabase.table("oportunidades").insert(
            [
                {
                    "negocio_id": negocio_id,
                    "tipo": oportunidad.tipo,
                    "motivo": oportunidad.motivo,
                    "prioridad": oportunidad.prioridad,
                }
                for oportunidad in analisis.oportunidades
            ]
        ).execute()

    return negocio_id


def guardar_fuente(negocio_id: str, tipo: str, url: str | None, datos: dict) -> None:
    supabase = cliente()
    if supabase is None or not negocio_id:
        return
    supabase.table("fuentes").insert(
        {"negocio_id": negocio_id, "tipo": tipo, "url": url, "datos": datos}
    ).execute()


def guardar_personas(personas: list[Persona]) -> int:
    supabase = cliente()
    if supabase is None or not personas:
        return 0

    filas = [
        {
            "nombre": persona.nombre,
            "cargo": persona.cargo,
            "empresa": persona.empresa,
            "ciudad": persona.ciudad,
            "email": persona.email,
            "linkedin": persona.linkedin,
        }
        for persona in personas
        if persona.linkedin
    ]
    if not filas:
        return 0

    respuesta = (
        supabase.table("personas").upsert(filas, on_conflict="tenant_id,linkedin").execute()
    )
    return len(respuesta.data or [])


def registrar_investigacion(tipo: str, consulta: dict, resultados: int) -> None:
    supabase = cliente()
    if supabase is None:
        return
    supabase.table("investigaciones").insert(
        {"tipo": tipo, "consulta": consulta, "resultados": resultados}
    ).execute()


# ─── Tareas en segundo plano ─────────────────────────────────────────


def crear_tarea(tipo: str, datos: dict) -> str | None:
    supabase = cliente()
    if supabase is None:
        return None
    respuesta = (
        supabase.table("tareas")
        .insert({"tipo": tipo, "datos": datos, "estado": "pendiente"})
        .execute()
    )
    return respuesta.data[0]["id"] if respuesta.data else None


def actualizar_tarea(
    tarea_id: str | None,
    estado: str,
    resultado: dict | None = None,
    error: str | None = None,
) -> None:
    supabase = cliente()
    if supabase is None or not tarea_id:
        return
    from datetime import datetime, timezone

    supabase.table("tareas").update(
        {
            "estado": estado,
            "resultado": resultado,
            "error": error,
            "actualizado_en": datetime.now(timezone.utc).isoformat(),
        }
    ).eq("id", tarea_id).execute()


def leer_tarea(tarea_id: str) -> dict | None:
    supabase = cliente()
    if supabase is None:
        return None
    respuesta = supabase.table("tareas").select("*").eq("id", tarea_id).limit(1).execute()
    return respuesta.data[0] if respuesta.data else None


def mejores_negocios(limite: int = 20, ciudad: str | None = None) -> list[dict]:
    supabase = cliente()
    if supabase is None:
        return []
    consulta = (
        supabase.table("negocios")
        .select("*")
        .eq("es_cliente", False)
        .order("puntuacion", desc=True)
        .limit(limite)
    )
    if ciudad:
        consulta = consulta.eq("ciudad", ciudad)
    return consulta.execute().data or []


def obtener_negocio(negocio_id: str) -> dict | None:
    """Obtiene un prospecto por id para una operación interna protegida."""
    supabase = cliente()
    if supabase is None:
        return None
    respuesta = (
        supabase.table("negocios")
        .select("*")
        .eq("id", negocio_id)
        .limit(1)
        .execute()
    )
    return respuesta.data[0] if respuesta.data else None
