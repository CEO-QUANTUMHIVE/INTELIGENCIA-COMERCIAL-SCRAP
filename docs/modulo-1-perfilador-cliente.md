# Módulo 1 — Perfilador de Clientes

**Guía de integración y de uso.** Este documento es el contrato de este
módulo hacia afuera: sirve para dárselo tal cual al equipo de **Fábrica de
Webs** (o de **Fábrica de Agentes**, que consume exactamente lo mismo), y
también es la referencia que cualquier agente de IA que trabaje en este repo
o en uno que se conecte a él debería leer antes de tocar este módulo.

---

## 1. Resumen para decisión

**Qué es:** un servicio HTTP que, dado el nombre y las redes de un cliente
que ya contrató, visita públicamente su web, Instagram, Facebook y/o su
ficha de Google Maps, y devuelve una ficha estructurada — contacto,
servicios, precios, horarios, preguntas frecuentes, competidores
mencionados, **y una base de identidad visual** (logo/foto de perfil +
colores dominantes) — lista para que la Fábrica de Webs arme el sitio del
cliente sin que alguien tenga que copiar y pegar esa información a mano.

> Para **Fábrica de Agentes** el contenido de texto ya alcanza tal cual
> (nombre, servicios, precios, horarios, FAQ). Para **Fábrica de Webs**,
> que además necesita arrancar con algo visual, el paquete suma
> `marca.logo_url` y `marca.colores` — ver [sección 4](#4-el-endpoint).

**Qué gana Fábrica de Webs:** onboarding de cliente más rápido. En vez de
mandarle un formulario largo al cliente nuevo, le piden nombre + Instagram
(o web, o Facebook, o el link de Maps) y este módulo devuelve un borrador
del contenido del sitio para completar/corregir, no para arrancar de cero.

**Qué tiene que hacer el equipo de Fábrica de Webs:**
1. Guardar una URL y un token que les va a pasar QuantumHive.
2. Desde **su backend** (no desde el navegador del cliente final), llamar a
   un único endpoint: `POST /clientes/investigar`.
3. Mapear la respuesta (JSON) a los campos de su generador de sitios.

**Qué no tienen que hacer:** scraping propio, llamadas a IA propias, ni
manejar Instagram/Facebook/Maps — todo eso ya lo resuelve este módulo.

**Estado:** el servicio base está en Cloud Run
(`https://perfilador-clientes-854335368640.us-east1.run.app`) con IA y
Supabase configurados, pero la revisión publicada todavía es anterior al
Dashboard y al Cazador de Recursos: la raíz devuelve 404 y esas rutas no
figuran en el OpenAPI de producción. Falta desplegar esta copia de trabajo.
Ver [sección 6](#6-checklist-de-activación).

---

## 2. Qué hace exactamente, paso a paso

```
Fábrica de Webs (su backend)
        │
        │  POST /clientes/investigar { nombre, web?, instagram?, facebook?, url_maps? }
        ▼
Centro de Inteligencia Comercial (este repo)
        │
        ├─ 1. Si hay url_maps → lee la ficha de Google Maps (teléfono, dirección, reseñas)
        ├─ 2. Si hay web → la visita (HTTP directo, o navegador stealth si el sitio bloquea)
        │       └─ saca: email, WhatsApp, redes, tecnología del sitio, si tiene chatbot,
        │          si tiene reservas online, el logo (og:image o favicon), y el texto
        ├─ 3. Si hay instagram → lee bio, cantidad de seguidores y foto de perfil (público)
        ├─ 4. Si hay facebook → lee nombre, descripción e imagen de la página (público)
        ├─ 5. Con todo el texto reunido, le pide a la IA (Claude u OpenAI, lo que
        │       tenga configurado QuantumHive) que arme: servicios, precios, horarios,
        │       preguntas frecuentes y competidores — SOLO lo que esté explícito en el
        │       texto. Si no hay IA configurada, o el sitio no tenía esa info, esos
        │       campos vuelven vacíos: nunca se inventa un precio o servicio.
        ├─ 6. Con el logo que haya encontrado (prioridad: web propia > Instagram >
        │       Facebook), calcula sus colores dominantes analizando la imagen.
        └─ 7. Guarda el cliente en la base de QuantumHive (para tener historial) y
                devuelve el JSON completo.
        ▼
Respuesta 200 con el paquete completo (ver sección 4)
```

**Tiempo de respuesta:** no es instantáneo — hace scraping real y una
llamada a IA. Normalmente entre 5 y 30 segundos; puede llegar a ~45s si el
sitio del cliente bloquea el scraping directo y hay que reintentar con
navegador. Diseñen la UI de Fábrica de Webs con un estado de carga
("Buscando info pública de tu negocio..."), no como una respuesta
instantánea de formulario.

---

## 3. Arquitectura de la conexión

```
┌─────────────────────┐        HTTPS + Bearer token        ┌──────────────────────────┐
│   Fábrica de Webs    │ ──────────────────────────────────▶│  Centro de Inteligencia  │
│   (SU backend/API)   │◀────────────────────────────────── │  Comercial (este repo)   │
└─────────────────────┘         JSON (PaquetePerfilCliente) └──────────────────────────┘
         ▲
         │  el navegador del cliente NUNCA le habla
         │  directo a este servicio
┌─────────────────────┐
│  Landing / navegador │
│  del cliente final   │
└─────────────────────┘
```

**Importante — llamar server-to-server, no desde el navegador.** El token
de autenticación no debe viajar al frontend. Si el formulario de la landing
corre en el navegador del cliente, ese formulario le pega a **su** backend
(el de Fábrica de Webs), y es ese backend el que le pega a este servicio con
el token guardado en su propio `.env`/secret manager. Nunca pongan
`CENTRO_INTELIGENCIA_TOKEN` en código de frontend ni en variables `NEXT_PUBLIC_*`
/ `VITE_*` (esas terminan en el bundle del navegador).

---

## 4. El endpoint

### `POST /clientes/investigar`

**Headers**

```
Content-Type: application/json
Authorization: Bearer <CENTRO_INTELIGENCIA_TOKEN>
```

El header `Authorization` solo es obligatorio si QuantumHive configuró
`TOKEN_INTERNO` en su despliegue (ver [sección 6](#6-checklist-de-activación)).
Si no lo hizo, el endpoint responde igual sin pedir nada — pero eso es solo
aceptable en desarrollo local, nunca en producción.

**Body** (`application/json`)

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `nombre` | string | **Sí** | Nombre del cliente/negocio |
| `web` | string \| null | No | URL de su sitio |
| `instagram` | string \| null | No | URL o `@usuario` de Instagram |
| `facebook` | string \| null | No | URL de su página de Facebook |
| `url_maps` | string \| null | No | Link a su ficha de Google Maps |

Al menos `nombre` es obligatorio. El resto es opcional, pero **cuantos más
tengan, mejor sale el perfil** — con solo el nombre, el sistema devuelve la
ficha casi vacía porque no tiene de dónde sacar información.

Ejemplo de request:

```json
{
  "nombre": "Barbería El Zorro",
  "web": "https://barberiaelzorro.com.ar",
  "instagram": "https://instagram.com/elzorro.barberia",
  "facebook": "https://facebook.com/elzorro.barberia",
  "url_maps": null
}
```

**Respuesta 200** — objeto `PaquetePerfilCliente`:

```json
{
  "negocio": {
    "nombre": "Barbería El Zorro",
    "categoria": "Barbería",
    "direccion": "Av. Corrientes 1234",
    "ciudad": null,
    "telefono": "+541145678900",
    "whatsapp": "+541145678900",
    "email": "info@barberiaelzorro.com.ar",
    "web": "https://barberiaelzorro.com.ar",
    "instagram": "https://instagram.com/elzorro.barberia",
    "facebook": "https://facebook.com/elzorro.barberia",
    "linkedin": null,
    "puntuacion_google": 4.7,
    "cantidad_resenas": 132,
    "url_maps": null,
    "latitud": null,
    "longitud": null,
    "web_funciona": true,
    "web_es_vieja": false,
    "web_es_plataforma": false,
    "tiene_chatbot": false,
    "tiene_reservas_online": true,
    "tecnologias": ["WordPress"],
    "texto_web": "texto completo de la página, recortado a ~6000 caracteres",
    "logo_url": "https://barberiaelzorro.com.ar/wp-content/logo.png"
  },
  "servicios": ["Corte clásico", "Arreglo de barba", "Coloración"],
  "precios": ["Corte $8000", "Barba $4000"],
  "horarios": "Lunes a sábado de 9 a 19",
  "preguntas_frecuentes": [
    {"pregunta": "¿Hay que sacar turno?", "respuesta": "Sí, por WhatsApp o la web"}
  ],
  "marca": {
    "logo_url": "https://barberiaelzorro.com.ar/wp-content/logo.png",
    "colores": ["#1a1a2e", "#e94560", "#f5f5f5", "#0f3460"],
    "bio_instagram": "El mejor corte del barrio desde 1998 ✂️",
    "seguidores": 3400,
    "descripcion_facebook": "Barbería tradicional en Almagro",
    "tecnologias": ["WordPress"]
  },
  "competidores": []
}
```

`preguntas_frecuentes` es una lista de objetos `{pregunta, respuesta}`.
`competidores` casi siempre viene vacío salvo que el propio negocio se
compare con otro explícitamente en su texto — no es (todavía) un buscador
de competidores, es best-effort sobre lo ya scrapeado.

**`marca.logo_url` y `marca.colores` — la parte visual, para Fábrica de
Webs.** `logo_url` es la URL pública de la imagen (og:image de la web, o si
no había, favicon de la web, o si tampoco, la foto de perfil de
Instagram/Facebook) — **no se descarga ni se re-hostea**, es la URL
original: bájenla ustedes cuando armen el sitio. `colores` son hasta 4
colores dominantes de esa imagen en hex (`#rrggbb`), ordenados de más a
menos presente — pensado como punto de partida para la paleta del sitio, no
como una decisión de diseño final. Si no se encontró ninguna imagen pública,
o la imagen no se pudo procesar, `logo_url` es `null` y `colores` es `[]` —
en ese caso hay que pedirle el logo al cliente a mano, como se hacía antes
de este módulo.

**Un campo vacío no es un error.** `servicios: []`, `horarios: null`,
`competidores: []`, `marca.colores: []` significan "no encontré esto
públicamente", no "falló algo". El sistema tiene la regla explícita de no
inventar precios, servicios ni identidad visual que el cliente no tiene —
mejor un campo vacío para completar a mano con el cliente que un dato falso
en su web.

---

## 5. Errores y cómo manejarlos

| Código | Cuándo pasa | Qué hacer del lado de Fábrica de Webs |
|---|---|---|
| `400` | Falta `nombre` en el body | Validar en su propio formulario antes de llamar |
| `401` | Falta el header `Authorization` o el token no coincide (solo si QuantumHive configuró `TOKEN_INTERNO`) | Revisar que el token guardado sea el vigente — QuantumHive avisa si lo rota |
| `500` / timeout / conexión caída | Caso raro — el módulo ya tiene fallbacks para que el scraping o la IA fallando no rompan la respuesta, pero una caída de red total del lado del Centro sigue siendo posible | Reintentar una vez; si vuelve a fallar, mostrarle al operador la opción de cargar el perfil a mano en vez de bloquear el onboarding |

Recomendación concreta de implementación: timeout de cliente de **60
segundos** como mínimo, y un solo reintento automático — no más, para no
scrapear el mismo sitio varias veces en paralelo sin necesidad.

---

## 6. Checklist de activación

**De parte de QuantumHive (para dejar el servicio listo):**

- [x] Servicio base desplegado en Cloud Run: `perfilador-clientes`, proyecto
      `bubbly-stone-502214-u7`, región `us-east1` (junto al resto de la
      infraestructura de QuantumHive)
- [ ] Publicar una revisión nueva con el Dashboard y el Cazador de Recursos
- [x] `TOKEN_INTERNO` seteado (Secret Manager)
- [x] IA configurada (proveedor compatible con la API de OpenAI, vía
      `OPENAI_BASE_URL`) — `servicios`/`precios`/`horarios`/
      `preguntas_frecuentes`/`competidores` se completan de verdad
- [x] Supabase conectado — cada llamada queda guardada, con historial
- [ ] Pasarle a Fábrica de Webs: la URL pública y el valor de `TOKEN_INTERNO`
      (por un canal seguro, no por chat en texto plano si se puede evitar)

**De parte de Fábrica de Webs:**

- [ ] Guardar `CENTRO_INTELIGENCIA_URL` y `CENTRO_INTELIGENCIA_TOKEN` como
      variables de entorno de **su backend** (nunca en el frontend)
- [ ] Implementar la llamada a `POST /clientes/investigar` desde ahí (ver
      ejemplo de código abajo)
- [ ] Mostrar un estado de carga en la UI (puede tardar hasta ~45s)
- [ ] Manejar `401`/`500`/timeout sin bloquear el onboarding — dejar cargar
      el perfil a mano como alternativa
- [ ] Mapear `servicios`, `precios`, `horarios`, `preguntas_frecuentes`,
      `marca`, `competidores` y los campos de `negocio` a los campos de su
      generador de sitios, dejando en claro en su propia UI cuáles son
      datos encontrados automáticamente y cuáles hay que completar (los que
      vinieron vacíos)

---

## 7. Ejemplos de código

**Node/JS (backend de la landing, no frontend):**

```js
async function perfilarCliente({ nombre, web, instagram, facebook, urlMaps }) {
  const respuesta = await fetch(`${process.env.CENTRO_INTELIGENCIA_URL}/clientes/investigar`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${process.env.CENTRO_INTELIGENCIA_TOKEN}`,
    },
    body: JSON.stringify({
      nombre,
      web: web ?? null,
      instagram: instagram ?? null,
      facebook: facebook ?? null,
      url_maps: urlMaps ?? null,
    }),
    signal: AbortSignal.timeout(60_000),
  });

  if (respuesta.status === 401) {
    throw new Error("Token de Centro de Inteligencia inválido o vencido.");
  }
  if (!respuesta.ok) {
    throw new Error(`Centro de Inteligencia respondió ${respuesta.status}`);
  }
  return respuesta.json(); // PaquetePerfilCliente
}
```

**curl (para probar a mano antes de integrar):**

```bash
curl -X POST https://TU-DEPLOY.example.com/clientes/investigar \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_TOKEN" \
  -d '{"nombre":"Barbería El Zorro","web":"https://barberiaelzorro.com.ar"}'
```

**Python (si Fábrica de Webs tiene algún worker/backend en Python):**

```python
import httpx

def perfilar_cliente(nombre, web=None, instagram=None, facebook=None, url_maps=None):
    respuesta = httpx.post(
        f"{CENTRO_INTELIGENCIA_URL}/clientes/investigar",
        headers={"Authorization": f"Bearer {CENTRO_INTELIGENCIA_TOKEN}"},
        json={"nombre": nombre, "web": web, "instagram": instagram,
              "facebook": facebook, "url_maps": url_maps},
        timeout=60,
    )
    respuesta.raise_for_status()
    return respuesta.json()
```

---

## 8. Para el que mantiene este módulo (referencia interna)

- Endpoint: [`aplicacion/api.py`](../aplicacion/api.py) → `POST /clientes/investigar`
- Orquestación: [`aplicacion/coordinador.py`](../aplicacion/coordinador.py) → `investigar_cliente()`
- Extracción de perfil (IA): [`aplicacion/ia/perfil_cliente.py`](../aplicacion/ia/perfil_cliente.py)
- Identidad visual (logo + colores): [`aplicacion/enriquecimiento/visual.py`](../aplicacion/enriquecimiento/visual.py)
  — usa Pillow (`requirements.txt`), no llamadas a IA ni servicios externos
- Forma de los datos: [`aplicacion/modelos.py`](../aplicacion/modelos.py) → `PaquetePerfilCliente`, `Negocio`
- Auth: `verificar_token()` en `api.py`, controlada por `TOKEN_INTERNO` en `configuracion.py`
- Cada llamada guarda (o actualiza) el cliente en la tabla `negocios` de
  Supabase con `es_cliente=true`, deduplicado por `url_maps` → `web` →
  `nombre|ciudad` (lo que haya, en ese orden). Llamar dos veces al mismo
  cliente actualiza su registro, no lo duplica.
- Pruebas: `pruebas/test_investigar_cliente.py`, `pruebas/test_perfil_cliente.py`,
  `pruebas/test_ia_generico.py`, `pruebas/test_visual.py`

Este mismo endpoint y contrato sirven, sin cambios, para la **Fábrica de
Agentes** (arma la knowledge base del agente de IA del cliente) — es el
mismo paquete, dos consumidores distintos.
