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

Le pasás nombre, web, Instagram o el link de Maps, y devuelve la ficha completa
más el paquete que consumen la Fábrica de Webs y la de Agentes.

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

(Sí, son dos navegadores: Playwright para Google Maps y Patchright — el que usa
Scrapling — para los sitios que bloquean bots. Se instalan una sola vez.)

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

| Método | Ruta | Qué hace |
|---|---|---|
| `GET` | `/salud` | Verifica qué está configurado |
| `POST` | `/buscar` | Busca negocios (en segundo plano, devuelve `tarea_id`) |
| `GET` | `/tareas/{id}` | Estado y resultado de la búsqueda |
| `POST` | `/investigar` | Investiga un negocio (responde directo) |
| `POST` | `/clientes/investigar` | Paquete para Fábrica de Webs / Agentes |
| `POST` | `/personas` | Decisores B2B |
| `GET` | `/negocios` | Mejores prospectos guardados |

```bash
curl -X POST http://localhost:8000/buscar \
  -H "Content-Type: application/json" \
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
│   ├── google_maps.py    ← Playwright (scrollea y entra a cada ficha)
│   ├── web.py            ← Scrapling (HTTP rápido, stealth si bloquean)
│   ├── instagram.py
│   ├── facebook.py
│   └── linkedin.py
│
├── enriquecimiento/    convierte datos crudos en información útil
│   ├── contactos.py      normaliza teléfonos, elige el mejor email
│   ├── negocio.py        completa la ficha visitando web y redes
│   └── oportunidades.py  arma el análisis comercial
│
├── ia/                 Claude u OpenAI, se elige por variable de entorno
│   ├── esquema.py        el contrato JSON y el prompt (compartido)
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
falla), `ia/__init__.py` puntúa con reglas simples. Sirve para probar el
pipeline entero gratis.

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

1. Conectar `investigar_cliente` con la Fábrica de Webs (generar demo + screenshot)
2. Conectar con la Fábrica de Agentes (armar knowledge base del cliente)
3. Outreach: WhatsApp y email primero, Instagram por la API oficial de Meta
4. LinkedIn Lead Gen Forms + Lead Sync API
