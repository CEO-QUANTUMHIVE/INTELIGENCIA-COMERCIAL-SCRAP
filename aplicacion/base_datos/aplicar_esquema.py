"""Aplica esquema.sql contra Supabase por conexión directa a Postgres.

Sirve para no depender nunca más del SQL Editor del navegador:

    python -m aplicacion.base_datos.aplicar_esquema

Necesita en el .env una de estas dos (con SUPABASE_DB_URL alcanza):

    SUPABASE_DB_URL=postgresql://postgres.xxxx:CLAVE@aws-0-....pooler.supabase.com:5432/postgres
    SUPABASE_DB_PASSWORD=la-clave-de-la-base

El esquema usa `create table if not exists`, así que se puede correr las veces
que haga falta: agrega lo que falta y no toca lo que ya está.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ARCHIVO_ESQUEMA = Path(__file__).parent / "esquema.sql"

TABLAS = ("negocios", "personas", "fuentes", "investigaciones", "oportunidades", "tareas")


def _referencia_proyecto() -> str:
    """Saca el project-ref de la URL: https://REF.supabase.co"""
    url = os.getenv("SUPABASE_URL", "")
    return url.replace("https://", "").split(".")[0]


def urls_a_probar() -> list[str]:
    """Las formas de conectarse, de la más específica a la más genérica."""
    explicita = os.getenv("SUPABASE_DB_URL", "").strip()
    if explicita:
        return [explicita]

    clave = os.getenv("SUPABASE_DB_PASSWORD", "").strip()
    ref = _referencia_proyecto()
    if not clave or not ref:
        return []

    from urllib.parse import quote

    clave_segura = quote(clave, safe="")
    candidatas = [
        # Conexión directa (IPv6 en proyectos nuevos)
        f"postgresql://postgres:{clave_segura}@db.{ref}.supabase.co:5432/postgres",
    ]
    # Pooler: funciona sobre IPv4. No sabemos la región, así que probamos las usuales.
    for region in ("us-east-1", "us-east-2", "us-west-1", "sa-east-1", "eu-central-1"):
        candidatas.append(
            f"postgresql://postgres.{ref}:{clave_segura}"
            f"@aws-0-{region}.pooler.supabase.com:5432/postgres"
        )
    return candidatas


def conectar():
    import psycopg

    candidatas = urls_a_probar()
    if not candidatas:
        print("Falta SUPABASE_DB_URL o SUPABASE_DB_PASSWORD en el .env.")
        sys.exit(1)

    ultimo_error = None
    for url in candidatas:
        visible = url.split("@")[-1]
        try:
            conexion = psycopg.connect(url, connect_timeout=15)
            print(f"Conectado a {visible}")
            return conexion
        except Exception as error:  # noqa: BLE001
            ultimo_error = error
            print(f"  no anduvo {visible}: {str(error).strip()[:90]}")

    print(f"\nNo se pudo conectar. Ultimo error: {ultimo_error}")
    sys.exit(1)


def main() -> int:
    sql = ARCHIVO_ESQUEMA.read_text(encoding="utf-8")
    print(f"Aplicando {ARCHIVO_ESQUEMA.name} ({len(sql)} caracteres)...\n")

    conexion = conectar()
    with conexion:
        with conexion.cursor() as cursor:
            cursor.execute(sql)
        conexion.commit()

        print("\nEsquema aplicado. Verificando tablas:")
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                select table_name
                from information_schema.tables
                where table_schema = 'public' and table_name = any(%s)
                order by table_name
                """,
                (list(TABLAS),),
            )
            encontradas = [fila[0] for fila in cursor.fetchall()]

    for tabla in TABLAS:
        print(f"  {'OK ' if tabla in encontradas else 'FALTA'} {tabla}")

    faltan = set(TABLAS) - set(encontradas)
    if faltan:
        print(f"\nFaltaron: {', '.join(sorted(faltan))}")
        return 1

    print(f"\nListo: las {len(TABLAS)} tablas estan creadas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
