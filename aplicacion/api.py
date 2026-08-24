"""API del Centro de Inteligencia Comercial.

Buscar negocios tarda minutos, así que /buscar corre en segundo plano y
devuelve un id de tarea. Investigar uno solo tarda segundos, así que va
sincrónico.
"""

import logging
import secrets
import uuid

from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException

from aplicacion import configuracion, coordinador
from aplicacion.base_datos import supabase
from aplicacion.modelos import PeticionBuscar, PeticionInvestigar, PeticionPersonas

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

app = FastAPI(
    title="Centro de Inteligencia Comercial — QuantumHive",
    version="0.1.0",
    description="Encuentra negocios, los investiga y dice qué venderles.",
)


def verificar_token(authorization: str | None = Header(default=None)) -> None:
    """Exige `Authorization: Bearer <TOKEN_INTERNO>` en los endpoints que
    tocan datos o disparan scraping. Si no hay TOKEN_INTERNO configurado (dev
    local) no exige nada, igual que el resto del sistema con Supabase/IA.
    """
    if not configuracion.TOKEN_INTERNO:
        return
    esperado = f"Bearer {configuracion.TOKEN_INTERNO}"
    if not authorization or not secrets.compare_digest(authorization, esperado):
        raise HTTPException(status_code=401, detail="Token inválido o faltante.")

# Respaldo para cuando no hay Supabase configurado todavía.
TAREAS_EN_MEMORIA: dict[str, dict] = {}


def _crear_tarea(tipo: str, datos: dict) -> str:
    tarea_id = supabase.crear_tarea(tipo, datos)
    if tarea_id:
        return tarea_id
    tarea_id = str(uuid.uuid4())
    TAREAS_EN_MEMORIA[tarea_id] = {
        "id": tarea_id,
        "tipo": tipo,
        "estado": "pendiente",
        "datos": datos,
        "resultado": None,
        "error": None,
    }
    return tarea_id


def _actualizar_tarea(tarea_id: str, estado: str, resultado=None, error=None) -> None:
    supabase.actualizar_tarea(tarea_id, estado, resultado, error)
    if tarea_id in TAREAS_EN_MEMORIA:
        TAREAS_EN_MEMORIA[tarea_id].update(
            {"estado": estado, "resultado": resultado, "error": error}
        )


def _correr_busqueda(tarea_id: str, peticion: PeticionBuscar) -> None:
    _actualizar_tarea(tarea_id, "corriendo")
    try:
        resultados = coordinador.buscar_negocios(
            rubro=peticion.rubro,
            ciudad=peticion.ciudad,
            cantidad=peticion.cantidad,
            analizar=peticion.analizar,
            guardar=peticion.guardar,
        )
        _actualizar_tarea(
            tarea_id,
            "lista",
            {
                "cantidad": len(resultados),
                "negocios": [r.model_dump(mode="json") for r in resultados],
            },
        )
    except Exception as error:  # noqa: BLE001
        logging.exception("Falló la búsqueda")
        _actualizar_tarea(tarea_id, "fallida", error=str(error))


@app.get("/salud")
def salud():
    return {
        "estado": "ok",
        "proveedor_ia": configuracion.PROVEEDOR_IA,
        "ia_configurada": configuracion.hay_ia(),
        "supabase_configurado": configuracion.hay_supabase(),
    }


@app.post("/buscar", dependencies=[Depends(verificar_token)])
def buscar(peticion: PeticionBuscar, tareas: BackgroundTasks):
    """Busca negocios en Google Maps, los enriquece y los puntúa.

    Corre en segundo plano: consultá /tareas/{id} para ver cómo va.
    """
    tarea_id = _crear_tarea("buscar", peticion.model_dump())
    tareas.add_task(_correr_busqueda, tarea_id, peticion)
    return {
        "tarea_id": tarea_id,
        "estado": "pendiente",
        "consultar_en": f"/tareas/{tarea_id}",
    }


@app.get("/tareas/{tarea_id}", dependencies=[Depends(verificar_token)])
def ver_tarea(tarea_id: str):
    tarea = supabase.leer_tarea(tarea_id) or TAREAS_EN_MEMORIA.get(tarea_id)
    if not tarea:
        raise HTTPException(status_code=404, detail="No existe esa tarea.")
    return tarea


@app.post("/investigar", dependencies=[Depends(verificar_token)])
def investigar(peticion: PeticionInvestigar):
    """Investiga un negocio puntual. Tarda segundos, responde directo."""
    if not any([peticion.nombre, peticion.web, peticion.instagram, peticion.url_maps]):
        raise HTTPException(
            status_code=400,
            detail="Pasá al menos uno: nombre, web, instagram o url_maps.",
        )
    return coordinador.investigar_negocio(
        nombre=peticion.nombre,
        web_url=peticion.web,
        instagram_url=peticion.instagram,
        facebook_url=peticion.facebook,
        url_maps=peticion.url_maps,
        guardar=peticion.guardar,
    )


@app.post("/clientes/investigar", dependencies=[Depends(verificar_token)])
def investigar_cliente(peticion: PeticionInvestigar):
    """Onboarding de un cliente: arma el paquete para Webs y Agentes."""
    if not peticion.nombre:
        raise HTTPException(status_code=400, detail="El nombre del cliente es obligatorio.")
    return coordinador.investigar_cliente(
        nombre=peticion.nombre,
        web_url=peticion.web,
        instagram_url=peticion.instagram,
        facebook_url=peticion.facebook,
        url_maps=peticion.url_maps,
    )


@app.post("/personas", dependencies=[Depends(verificar_token)])
def personas(peticion: PeticionPersonas):
    """Busca decisores B2B (perfiles públicos de LinkedIn vía buscador)."""
    return coordinador.buscar_personas(
        rubro=peticion.rubro,
        ciudad=peticion.ciudad,
        cargos=peticion.cargos,
        cantidad=peticion.cantidad,
    )


@app.get("/negocios", dependencies=[Depends(verificar_token)])
def listar_negocios(limite: int = 20, ciudad: str | None = None):
    """Los mejores prospectos guardados, ordenados por puntuación."""
    return supabase.mejores_negocios(limite=limite, ciudad=ciudad)
