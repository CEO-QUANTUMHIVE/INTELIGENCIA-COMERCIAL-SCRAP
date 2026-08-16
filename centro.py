"""Línea de comandos del Centro de Inteligencia Comercial.

Para probar sin levantar la API:

    python centro.py buscar barberías "Buenos Aires" --cantidad 20
    python centro.py investigar --web https://barberiax.com
    python centro.py personas gastronomía --ciudad Argentina
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from aplicacion import coordinador

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s %(message)s",
    datefmt="%H:%M:%S",
)

SALIDAS = Path("salidas")


def _guardar(nombre: str, datos) -> Path:
    SALIDAS.mkdir(exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d-%H%M%S")
    archivo = SALIDAS / f"{nombre}-{marca}.json"
    archivo.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    return archivo


def _mostrar_negocio(resultado, posicion: int | None = None) -> None:
    negocio = resultado.negocio
    analisis = resultado.analisis
    encabezado = f"{posicion}. " if posicion else ""
    puntos = f"  [{analisis.puntuacion}/100]" if analisis else ""

    print(f"\n{encabezado}{negocio.nombre}{puntos}")
    print(f"   {negocio.categoria or 'sin rubro'} · {negocio.direccion or 'sin dirección'}")
    print(
        f"   tel: {negocio.telefono or '—'} | web: {negocio.web or '—'} | "
        f"reseñas: {negocio.cantidad_resenas or 0}"
    )
    if analisis:
        if analisis.problemas:
            print(f"   problemas: {'; '.join(analisis.problemas[:3])}")
        if analisis.oferta_recomendada:
            print(f"   ofrecer: {', '.join(analisis.oferta_recomendada)}")


def comando_buscar(argumentos) -> int:
    resultados = coordinador.buscar_negocios(
        rubro=argumentos.rubro,
        ciudad=argumentos.ciudad,
        cantidad=argumentos.cantidad,
        analizar=not argumentos.sin_ia,
        guardar=not argumentos.sin_guardar,
    )

    if not resultados:
        print("\nNo se encontró nada. Probá con otro rubro o ciudad.")
        return 1

    print(f"\n{'=' * 60}\n{len(resultados)} negocios encontrados\n{'=' * 60}")
    for posicion, resultado in enumerate(resultados, start=1):
        _mostrar_negocio(resultado, posicion)

    archivo = _guardar(
        f"buscar-{argumentos.rubro}".replace(" ", "_"),
        [r.model_dump(mode="json") for r in resultados],
    )
    print(f"\nGuardado en {archivo}")
    return 0


def comando_investigar(argumentos) -> int:
    resultado = coordinador.investigar_negocio(
        nombre=argumentos.nombre,
        web_url=argumentos.web,
        instagram_url=argumentos.instagram,
        url_maps=argumentos.maps,
        guardar=not argumentos.sin_guardar,
    )
    _mostrar_negocio(resultado)

    if resultado.analisis and resultado.analisis.mensaje_sugerido:
        print(f"\nMensaje sugerido:\n{resultado.analisis.mensaje_sugerido}")

    archivo = _guardar("investigar", resultado.model_dump(mode="json"))
    print(f"\nGuardado en {archivo}")
    return 0


def comando_personas(argumentos) -> int:
    personas = coordinador.buscar_personas(
        rubro=argumentos.rubro,
        ciudad=argumentos.ciudad,
        cantidad=argumentos.cantidad,
    )
    if not personas:
        print("\nNo se encontraron decisores.")
        return 1

    print(f"\n{len(personas)} decisores encontrados:\n")
    for persona in personas:
        print(f"  {persona.nombre} — {persona.cargo or '?'} en {persona.empresa or '?'}")
        print(f"     {persona.linkedin}")

    archivo = _guardar("personas", [p.model_dump(mode="json") for p in personas])
    print(f"\nGuardado en {archivo}")
    return 0


def main() -> int:
    analizador = argparse.ArgumentParser(description="Centro de Inteligencia Comercial")
    subcomandos = analizador.add_subparsers(dest="comando", required=True)

    buscar = subcomandos.add_parser("buscar", help="Buscar negocios en Google Maps")
    buscar.add_argument("rubro")
    buscar.add_argument("ciudad")
    buscar.add_argument("--cantidad", type=int, default=20)
    buscar.add_argument("--sin-ia", action="store_true", help="No llamar a la IA")
    buscar.add_argument("--sin-guardar", action="store_true", help="No escribir en Supabase")
    buscar.set_defaults(funcion=comando_buscar)

    investigar = subcomandos.add_parser("investigar", help="Investigar un negocio")
    investigar.add_argument("--nombre")
    investigar.add_argument("--web")
    investigar.add_argument("--instagram")
    investigar.add_argument("--maps")
    investigar.add_argument("--sin-guardar", action="store_true")
    investigar.set_defaults(funcion=comando_investigar)

    personas = subcomandos.add_parser("personas", help="Buscar decisores B2B")
    personas.add_argument("rubro")
    personas.add_argument("--ciudad")
    personas.add_argument("--cantidad", type=int, default=20)
    personas.set_defaults(funcion=comando_personas)

    argumentos = analizador.parse_args()
    return argumentos.funcion(argumentos)


if __name__ == "__main__":
    sys.exit(main())
