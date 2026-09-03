"""Pruebas para el módulo de Cazador de Recursos, Créditos y Beneficios Educativos."""

import pytest
from fastapi.testclient import TestClient

from aplicacion.api import app
from aplicacion.modelos_recursos import (
    CategoriaRecurso,
    FiltroRecursos,
    PeticionPostulacion,
    TipoCorreoRequerido,
)
from aplicacion.recursos.catalogo import (
    CATALOGO_RECURSOS,
    filtrar_recursos,
    obtener_recurso,
)
from aplicacion.recursos.postulador import generar_postulacion

cliente = TestClient(app)


def test_catalogo_no_vacio():
    assert len(CATALOGO_RECURSOS) >= 10
    recursos_ids = [r.id for r in CATALOGO_RECURSOS]
    assert "github-student-pack" in recursos_ids
    assert "microsoft-founders-hub" in recursos_ids
    assert "nvidia-inception" in recursos_ids


def test_filtro_correo_estudiante():
    filtro = FiltroRecursos(tiene_correo_estudiante=True, tiene_correo_corporativo=False)
    resultados = filtrar_recursos(filtro)

    assert len(resultados) > 0
    # No debe incluir recursos que exijan EXCLUSIVAMENTE correo corporativo
    for r in resultados:
        assert r.correo_requerido in (
            TipoCorreoRequerido.ESTUDIANTE,
            TipoCorreoRequerido.CUALQUIERA,
        )


def test_filtro_correo_corporativo():
    filtro = FiltroRecursos(tiene_correo_estudiante=False, tiene_correo_corporativo=True)
    resultados = filtrar_recursos(filtro)

    assert len(resultados) > 0
    # No debe incluir recursos que exijan EXCLUSIVAMENTE correo de estudiante
    for r in resultados:
        assert r.correo_requerido in (
            TipoCorreoRequerido.CORPORATIVO,
            TipoCorreoRequerido.CUALQUIERA,
        )


def test_filtro_categoria_cloud():
    filtro = FiltroRecursos(categoria=CategoriaRecurso.CLOUD)
    resultados = filtrar_recursos(filtro)

    assert len(resultados) > 0
    for r in resultados:
        assert r.categoria == CategoriaRecurso.CLOUD


def test_busqueda_texto():
    filtro = FiltroRecursos(texto_busqueda="NVIDIA")
    resultados = filtrar_recursos(filtro)

    assert len(resultados) >= 1
    assert any(r.id == "nvidia-inception" for r in resultados)


def test_generador_postulacion_estudiante(monkeypatch):
    monkeypatch.setattr(
        "aplicacion.recursos.postulador.analizar_con_esquema", lambda *a, **k: None
    )
    peticion = PeticionPostulacion(
        recurso_id="azure-for-students",
        nombre_proyecto="Detector de Plagas con IA",
        descripcion_proyecto="Modelo de visión por computadora para detectar enfermedades en cultivos",
        tipo_postulante="estudiante",
        correo_a_usar="alumno@universidad.edu.ar",
        stack_tecnologico=["Python", "PyTorch", "FastAPI"],
    )
    resultado = generar_postulacion(peticion)

    assert resultado.recurso_id == "azure-for-students"
    assert len(resultado.pitch_elevator) > 20
    assert len(resultado.caso_de_uso_creditos) > 20
    assert len(resultado.checklist_antes_de_enviar) >= 1
    assert "azure" in resultado.url_postulacion.lower()
    assert resultado.generado_con_ia is False


def test_generador_postulacion_startup_corp(monkeypatch):
    monkeypatch.setattr(
        "aplicacion.recursos.postulador.analizar_con_esquema", lambda *a, **k: None
    )
    peticion = PeticionPostulacion(
        recurso_id="microsoft-founders-hub",
        nombre_proyecto="QuantumHive Commercial AI",
        descripcion_proyecto="Plataforma de agentes de inteligencia comercial",
        tipo_postulante="startup",
        correo_a_usar="contacto@quantumhive.com",
        stack_tecnologico=["Python", "FastAPI", "Docker", "Azure"],
    )
    resultado = generar_postulacion(peticion)

    assert resultado.recurso_id == "microsoft-founders-hub"
    assert len(resultado.pitch_elevator) > 20
    assert len(resultado.arquitectura_tecnica) > 20


def test_endpoint_dashboard_html():
    respuesta = cliente.get("/")
    assert respuesta.status_code == 200
    assert "text/html" in respuesta.headers["content-type"]
    assert "QuantumHive" in respuesta.text
    assert "Cazador de Recursos" in respuesta.text


def test_endpoint_api_recursos_es_publico_aun_con_token_configurado(monkeypatch):
    monkeypatch.setattr("aplicacion.configuracion.TOKEN_INTERNO", "token-privado")
    respuesta = cliente.get("/api/recursos?tiene_correo_estudiante=true")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert isinstance(datos, list)
    assert len(datos) > 0


def test_endpoint_postular_sigue_protegido_con_token_configurado(monkeypatch):
    monkeypatch.setattr("aplicacion.configuracion.TOKEN_INTERNO", "token-privado")
    respuesta = cliente.post(
        "/api/recursos/postular",
        json={
            "recurso_id": "github-student-pack",
            "nombre_proyecto": "Portfolio Web",
            "descripcion_proyecto": "Sitio para proyectos de código abierto",
            "correo_a_usar": "test@edu.ar",
        },
    )
    assert respuesta.status_code == 401


def test_endpoint_api_postular(monkeypatch):
    monkeypatch.setattr(
        "aplicacion.recursos.postulador.analizar_con_esquema", lambda *a, **k: None
    )
    payload = {
        "recurso_id": "github-student-pack",
        "nombre_proyecto": "Portfolio Web",
        "descripcion_proyecto": "Sitio web interactivo para proyectos de código abierto",
        "tipo_postulante": "estudiante",
        "correo_a_usar": "test@edu.ar",
        "stack_tecnologico": ["React", "Python"],
    }
    respuesta = cliente.post("/api/recursos/postular", json=payload)
    assert respuesta.status_code == 200
    data = respuesta.json()
    assert data["recurso_id"] == "github-student-pack"
    assert "pitch_elevator" in data
    assert len(data["checklist_antes_de_enviar"]) >= 1
    assert data["generado_con_ia"] is False
