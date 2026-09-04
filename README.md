# Centro de Inteligencia Comercial — QuantumHive

Encuentra negocios, los investiga, y dice qué venderles.

Es el módulo que alimenta a la **Fábrica de Webs**, la **Fábrica de Agentes** y a
los agentes comerciales de QuantumHive.

---

## Qué hace hoy

**A) Buscar clientes nuevos**

```
"Buscá 20 barberías de Buenos Aires"
        ↓
Google Maps → web → Instagram/Facebook
        ↓
teléfono, WhatsApp, email, redes, tecnología del sitio
        ↓
IA: puntuación 0-100 + problemas + qué ofrecerle + mensaje sugerido
        ↓
Supabase
```

**B) Investigar un negocio puntual (prospecto o cliente)**

Le pasás nombre, web, Instagram, Facebook o el link de Maps, y devuelve la
ficha completa más el paquete que consumen la Fábrica de Webs y la de
Agentes: negocio, marca, servicios, precios, horarios, preguntas frecuentes
y competidores mencionados — esto vía IA sobre lo que ya se scrapeó (nunca
inventa: si no está en el texto, queda vacío) — más logo y colores
dominantes (esto no depende de IA, es análisis de imagen puro: funciona
incluso sin ninguna clave configurada).

> **Este es el "Módulo 1 — Perfilador de Clientes".** Guía completa de
> integración (contrato de la API, ejemplos de código, checklist de
> activación) en
> [`docs/modulo-1-perfilador-cliente.md`](docs/modulo-1-perfilador-cliente.md) —
> es el documento para pasarle al equipo de Fábrica de Webs o de Fábrica de
> Agentes.

**C) Decisores B2B**

Busca dueños, CEOs y directores por rubro y ciudad.

---

## Arranque rápido (5 minutos)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
patchright install chromium
```

(`playwright install` deja los binarios base; `patchright install` instala el
Chromium parcheado anti-detección que usan tanto Google Maps como Scrapling
—vía `StealthyFetcher`— para los sitios que bloquean bots. Se instalan una
sola vez.)

```bash
copy .env.example .env
```

Editá `.env` y poné, como mínimo, `ANTHROPIC_API_KEY` (o `OPENAI_API_KEY` con
`PROVEEDOR_IA=openai`). Supabase podés dejarlo vacío al principio: el sistema
funciona igual, solo que no guarda.

Primera prueba, sin base de datos y sin gastar en IA:

```bash
python centro.py buscar barberías "Buenos Aires" --cantidad 5 --sin-ia --sin-guardar
```

Si eso te devuelve 5 barberías con teléfono y web, el scraping anda. Ahora con IA:

```bash
python centro.py buscar barberías "Buenos Aires" --cantidad 20
```

Cada corrida deja un JSON en `salidas/`.

---

## La base de datos

En Supabase → **SQL Editor** → pegá entero
[`aplicacion/base_datos/esquema.sql`](aplicacion/base_datos/esquema.sql) y ejecutá.

Son 6 tablas: `negocios`, `personas`, `fuentes`, `investigaciones`,
`oportunidades`, `tareas`. Cuando aparezca una necesidad real agregamos más;
antes no.

(Todas llevan `tenant_id` con un valor por defecto. Es una columna, no cuesta
nada, y evita una migración fea el día que haya más de un cliente usando esto.)

Después completá `SUPABASE_URL` y `SUPABASE_KEY` en `.env` — usá la
**service_role key**, porque acá escribe el backend, no un cliente público.

---

## La API

```bash
uvicorn aplicacion.api:app --reload
```

Documentación interactiva en <http://localhost:8000/docs>.

| Método | Ruta | Qué hace | Requiere token |
|---|---|---|---|
| `GET` | `/salud` | Verifica qué está configurado | No |
| `GET` | `/api/recursos` | Lista el catálogo estático de créditos y beneficios | No |
| `POST` | `/api/recursos/postular` | Genera el borrador de una postulación | Sí |
| `POST` | `/api/recursos/cazar-web` | Busca oportunidades nuevas en la web | Sí |
| `POST` | `/buscar` | Busca negocios (en segundo plano, devuelve `tarea_id`) | Sí |
| `GET` | `/tareas/{id}` | Estado y resultado de la búsqueda | Sí |
| `POST` | `/investigar` | Investiga un negocio (responde directo) | Sí |
| `POST` | `/clientes/investigar` | Paquete para Fábrica de Webs / Agentes | Sí |
| `POST` | `/personas` | Decisores B2B | Sí |
| `GET` | `/negocios` | Mejores prospectos guardados | Sí |

Si configurás `TOKEN_INTERNO` en `.env`, las operaciones que disparan IA,
scraping o acceden a datos internos exigen el header
`Authorization: Bearer <TOKEN_INTERNO>` — así es como la Fábrica de Webs y la
Fábrica de Agentes consumen esta API sin dejarla abierta. El catálogo estático
`GET /api/recursos` es público para que la landing pueda mostrar los programas
sin exponer el token. Con `TOKEN_INTERNO` vacío (default en desarrollo local)
las operaciones protegidas tampoco piden token.

El cazador prioriza `APIFY_BUSQUEDA_ACTOR` (por defecto, el Actor oficial
`apify/google-search-scraper`) y consulta una sola página por búsqueda. El
parámetro `APIFY_BUSQUEDA_MAX_COSTO_USD` limita cada ejecución; Apify exige un
mínimo de `0.50` para ese tope, aunque una consulta normal consume solo una
fracción de ese importe. Si Apify no está configurado o falla, se intenta el
lector público de DuckDuckGo como respaldo.

```bash
curl -X POST http://localhost:8000/buscar \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN_INTERNO" \
  -d "{\"rubro\":\"barberías\",\"ciudad\":\"Buenos Aires\",\"cantidad\":20}"
```

---

## Cómo está armado

```
aplicacion/
├── api.py              FastAPI
├── coordinador.py      el agente único: junta todo
├── configuracion.py    variables de entorno
├── modelos.py          las formas de los datos
│
├── buscadores/         hablan con cada fuente
│   ├── google_maps.py    ← Patchright (scrollea y entra a cada ficha, anti-detección)
│   ├── web.py            ← Scrapling (HTTP rápido, stealth si bloquean)
│   ├── instagram.py
│   ├── facebook.py
│   └── linkedin.py
│
├── enriquecimiento/    convierte datos crudos en información útil
│   ├── contactos.py      normaliza teléfonos, elige el mejor email
│   ├── negocio.py        completa la ficha visitando web y redes
│   ├── oportunidades.py  arma el análisis comercial
│   └── visual.py         logo + colores dominantes (sin IA, análisis de imagen)
│
├── ia/                 Claude u OpenAI, se elige por variable de entorno
│   ├── __init__.py       analizar_con_esquema(): primitiva genérica compartida
│   ├── esquema.py        contrato JSON + prompt del scoring comercial
│   ├── perfil_cliente.py contrato JSON + prompt del paquete de onboarding
│   ├── claude.py
│   └── openai.py
│
└── base_datos/
    ├── supabase.py
    └── esquema.sql
```

Se entiende mirando la carpeta 30 segundos. Esa es la idea.

---

## Decisiones que conviene conocer

**LinkedIn no se scrapea.** LinkedIn prohíbe expresamente el scraping y
restringe las cuentas que lo hacen. `linkedin.py` busca en un buscador web los
perfiles públicos que LinkedIn ya indexó, y de ahí saca nombre, cargo y empresa.
Después el resto del sistema investiga la empresa por su web y sus redes, que es
donde está lo que sirve. Para volumen serio, la vía oficial es Sales Navigator +
Lead Gen Forms + Lead Sync API, y ese conector va al lado de este archivo, no en
lugar de él.

**Google Maps sí se scrapea.** Es gratis e ilimitado y trae reseñas, web y
teléfono. Se rompe cuando Google cambia el HTML: los selectores están todos
juntos en `_leer_ficha()`, así que arreglarlo es tocar un lugar. Si algún día
molesta, se agrega un adaptador de Places API al lado.

**Una "web" que es un perfil ajeno cuenta como no tener web.** Muchísimos
negocios ponen en Google Maps su link de Agendapro, Calendly o Linktree. Si lo
tomáramos como su sitio, quedarían marcados como "ya tiene web moderna con
reservas online" y los descartaríamos — cuando en realidad son los mejores
prospectos que hay. `web.es_plataforma()` los detecta, los puntúa como si no
tuvieran web, y evita que les copiemos el Instagram y los mails de la
plataforma. La lista de plataformas está en `buscadores/web.py`; agregá las que
falten a medida que aparezcan.

**Sin IA el sistema igual funciona.** Si no hay clave configurada (o la llamada
falla), `ia/__init__.py` puntúa con reglas simples para el scoring comercial, y
`ia/perfil_cliente.py` devuelve el paquete con esos campos vacíos en vez de
inventar servicios o precios que el cliente no tiene. Sirve para probar el
pipeline entero gratis y evita que la IA le mienta a la Fábrica de Webs.

**La API no está abierta por defecto.** `TOKEN_INTERNO` en `.env` protege las
operaciones internas y las que consumen scraping o IA. Sólo `/salud` y el
catálogo estático `/api/recursos` son públicos. Vacío en desarrollo local;
setealo antes de que la Fábrica de Webs o la Fábrica de Agentes la llamen
desde afuera.

**El modelo por defecto es `claude-opus-5`.** Para analizar cientos de negocios
por corrida, poné `MODELO_CLAUDE=claude-sonnet-5` en `.env`: mismo contrato,
bastante más barato.

---

## Pruebas

```bash
pytest
```

Cubren lo que se rompe en silencio: normalización de teléfonos, elección de
email y el motor de puntuación. El scraping no se testea con mocks — se prueba
corriéndolo.

---

## Qué sigue (cuando algo lo justifique, no antes)

1. ~~Que `investigar_cliente` arme el paquete completo~~ — listo: servicios,
   precios, horarios, FAQ y competidores se extraen vía IA de lo scrapeado.
   Contrato de integración documentado en
   [`docs/modulo-1-perfilador-cliente.md`](docs/modulo-1-perfilador-cliente.md).
   Falta que Fábrica de Webs (generar demo + screenshot) y Fábrica de Agentes
   (knowledge base del cliente) lo consuman de su lado — vive en esos repos.
2. Outreach: WhatsApp y email primero, Instagram/Facebook por la API oficial
   de Meta vía Chatwoot (ver `docs/superpowers/specs/2026-08-17-outreach-chatwoot-design.md`)
3. Cazador de inversión y créditos: mismo motor, nuevo dominio (oportunidades
   de capital en vez de prospectos comerciales) + redactor de propuestas
4. LinkedIn Lead Gen Forms + Lead Sync API
