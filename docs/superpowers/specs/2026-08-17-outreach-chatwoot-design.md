# Outreach multicanal con Chatwoot como panel de control

**Fecha:** 2026-08-17
**Estado:** Aprobado para planificación

## Contexto

`INTELIGENCIA-COMERCIAL-SCRAP` hoy busca negocios (Google Maps), los enriquece
(web, Instagram, Facebook), los puntúa con IA y genera un `mensaje_sugerido`
por negocio — pero ese mensaje no se manda a ningún lado. Alguien tiene que
copiarlo y mandarlo a mano.

El objetivo de este spec es cerrar ese hueco: que el sistema pueda mandar (o
dejar listo para mandar) el primer contacto por Email, Instagram, Facebook y
WhatsApp, y que exista un panel donde auditar todo — agentes trabajando,
mensajes salientes, respuestas entrantes — sin construir una bandeja de
mensajería desde cero.

## Decisión: adoptar Chatwoot

Se investigaron tres opciones (ver discusión previa): construir un panel a
medida, orquestar con n8n, o adoptar un producto de bandeja omnicanal ya
armado. Se eligió **Chatwoot** (open source, self-hosteable,
https://github.com/chatwoot/chatwoot):

- Bandeja omnicanal nativa: WhatsApp (API oficial de Meta), Instagram DM,
  Facebook Messenger, Email, todo en una sola vista de conversaciones.
- API REST propia para crear contactos, conversaciones y mandar mensajes
  programáticamente.
- Panel de auditoría, roles, labels y asignación de agentes ya incluidos.
- Evita reconstruir un producto maduro (threading, adjuntos, estados de
  entrega) que llevaría semanas hacerlo a medida.

**Restricción de Meta que condiciona el diseño:** WhatsApp Business Cloud API
no permite mandar texto libre como primer mensaje a un contacto que nunca
escribió — exige plantillas pre-aprobadas para todo contacto en frío. Email,
Instagram DM y Facebook Messenger no tienen esa restricción para el primer
contacto.

## Decisión: quién manda el primer mensaje, por canal

- **Email / Instagram / Facebook** — automático. El módulo de outreach manda
  el `mensaje_sugerido` directo vía la API de Chatwoot apenas se aprueba el
  prospecto.
- **WhatsApp** — manual. En vez de pelear con la aprobación de plantillas de
  Meta, el primer contacto lo manda el dueño del negocio desde su número de
  WhatsApp **personal**, con un link `wa.me/<WHATSAPP_BUSINESS_NUMBER>?text=...`
  prellenado con el mensaje. Cuando el prospecto le escribe a ese número desde
  el link, la respuesta entra al WhatsApp Business real (dentro de Chatwoot) y
  ya no aplica la restricción de plantillas (ventana de 24hs abierta por el
  prospecto).

## Arquitectura

Tres piezas, cada una con un rol claro:

1. **Este repo** — motor de prospección. Sin cambios en lo que ya hace
   (scraping, enriquecimiento, scoring). Se agrega el módulo `aplicacion/outreach/`.
2. **Chatwoot** — servicio nuevo, self-hosted. Panel de control y bandeja
   omnicanal. No se modifica su código, se usa vía su API pública.
3. **Fábrica de Webs / Fábrica de Agentes** — fuera de este alcance. Cada una
   agrega su propia pestaña apuntando a la API de este repo. No se toca
   código de esos repos desde acá.

```
Google Maps / Web / IG / FB  →  scraping + enriquecimiento (ya existe)
        ↓
   Analisis.mensaje_sugerido (IA, ya existe)
        ↓
   aplicacion/outreach/  (nuevo)
        ↓
   ¿canal disponible?
     Email/IG/FB → Chatwoot API: crear contacto + conversación + mandar mensaje (automático)
     WhatsApp    → Chatwoot API: crear contacto + nota privada con mensaje + link wa.me (manual)
        ↓
   Chatwoot = panel único de auditoría y de respuestas entrantes
```

## Flujo de datos

1. `coordinador.buscar_negocios()` / `investigar_negocio()` corren como hoy:
   scraping → enriquecimiento → análisis IA → `Analisis.mensaje_sugerido`.
2. Al aprobar un prospecto para contactar (nuevo endpoint), `outreach/`
   decide el canal según qué contacto tiene el negocio (`email`, `instagram`,
   `facebook`, `telefono`/`whatsapp`) y llama a Chatwoot:
   - Si hay email/instagram/facebook: crea contacto + conversación + manda
     `mensaje_sugerido` como primer mensaje.
   - Si el único contacto es WhatsApp: crea contacto, postea el
     `mensaje_sugerido` + link `wa.me/...` como **nota privada** (no se envía
     al prospecto), etiqueta la conversación `whatsapp-pendiente-manual`.
3. Las respuestas del prospecto (por cualquier canal) entran solas al inbox
   de Chatwoot vía los webhooks de Meta — no requiere código nuestro.
4. **Fuera de alcance de este spec:** automatizar el seguimiento de
   conversaciones ya abiertas (webhook de Chatwoot hacia este repo para que
   la IA sugiera la respuesta). Queda anotado como fase 2.

## Componentes nuevos

- `aplicacion/outreach/chatwoot.py` — cliente HTTP delgado para la API de
  Chatwoot (crear contacto, crear conversación, mandar mensaje, postear nota
  privada, aplicar labels). Mismo patrón que
  [`aplicacion/base_datos/supabase.py`](../../../aplicacion/base_datos/supabase.py):
  si no hay `CHATWOOT_URL` / `CHATWOOT_API_KEY` configurados, avisa por log y
  no rompe el resto del sistema.
- Función de decisión de canal (en `aplicacion/outreach/` o dentro de
  `coordinador.py`) que, dado un `Negocio` + `Analisis`, arma el payload
  correcto para Chatwoot.
- Endpoint nuevo `POST /contactar/{negocio_id}` en
  [`aplicacion/api.py`](../../../aplicacion/api.py).
- Variables nuevas en `.env` / `configuracion.py`: `CHATWOOT_URL`,
  `CHATWOOT_API_KEY`, `CHATWOOT_ACCOUNT_ID`, `WHATSAPP_BUSINESS_NUMBER`.

## Manejo de errores

- Chatwoot no configurado → el sistema sigue funcionando igual que hoy sin
  Supabase: loguea y no manda nada, no rompe el flujo de scraping/análisis.
- Falla la llamada a la API de Chatwoot (servicio caído, rate limit) → un
  reintento; si vuelve a fallar, se guarda el intento pendiente (para
  reprocesar después) en vez de perder el mensaje.
- El cliente de Chatwoot **no expone** la opción de mandar WhatsApp frío por
  la API oficial sin plantilla — se omite a propósito del código para que
  nadie rompa sin querer la política de Meta.

## Testing

- `outreach/chatwoot.py` se testea con mocks, mismo criterio que
  [`pruebas/test_contactos.py`](../../../pruebas/test_contactos.py) — los
  tests automáticos no le pegan a una instancia real de Chatwoot.
- La decisión de canal (qué contacto usa cada negocio) se testea con casos
  puros, sin red, igual que `test_plataformas.py`.

## Prerequisitos operativos (no son código)

- Cuenta de Meta Business verificada + WhatsApp Business Cloud API conectada
  al número real del negocio.
- Instancia de Chatwoot self-hosted levantada y accesible (Docker), con los
  canales de Email, Facebook Page e Instagram Business conectados desde su
  propio panel de configuración.

## Fuera de alcance de este spec

- **Anti-detección en `google_maps.py`**: hoy usa Playwright puro sin parche
  anti-detección (a diferencia de `web.py`/`instagram.py`/`facebook.py`, que
  vía Scrapling ya corren sobre un motor basado en Patchright desde la
  versión 0.3.13). Cambiar el import de `playwright.sync_api` a
  `patchright.sync_api` en
  [`aplicacion/buscadores/google_maps.py`](../../../aplicacion/buscadores/google_maps.py)
  es un cambio de una línea (API idéntica) — se hace como tarea suelta, no
  necesita spec propio.
- Integración de pestañas en Fábrica de Webs / Fábrica de Agentes — vive en
  esos repos, no en este.
- Automatizar respuestas de seguimiento con IA (fase 2).
- Corrección del hallazgo de auditoría sobre RLS sin `tenant_id` en Supabase
  y falta de autenticación en la API — quedó pendiente de una decisión
  aparte, no forma parte de este spec.
