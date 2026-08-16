-- Centro de Inteligencia Comercial — esquema mínimo (6 tablas).
-- Pegar entero en el SQL Editor de Supabase y ejecutar.
-- Cuando aparezca una necesidad real, agregamos tablas. Antes no.

create extension if not exists "pgcrypto";

-- ─────────────────────────────────────────────────────────────────────
-- 1. NEGOCIOS — todo lo que encontramos, sea prospecto o cliente
-- ─────────────────────────────────────────────────────────────────────
create table if not exists negocios (
    id                    uuid primary key default gen_random_uuid(),
    tenant_id             text not null default 'quantumhive',
    clave                 text not null,          -- url_maps, o web, o nombre|ciudad
    es_cliente            boolean not null default false,

    nombre                text not null,
    categoria             text,
    direccion             text,
    ciudad                text,

    telefono              text,
    whatsapp              text,
    email                 text,
    web                   text,
    instagram             text,
    facebook              text,
    linkedin              text,

    puntuacion_google     numeric,
    cantidad_resenas      integer,
    url_maps              text,
    latitud               numeric,
    longitud              numeric,

    web_funciona          boolean,
    web_es_vieja          boolean,
    web_es_plataforma     boolean,   -- su "web" es un perfil ajeno: no tiene web propia

    tiene_chatbot         boolean,
    tiene_reservas_online boolean,
    tecnologias           jsonb default '[]'::jsonb,

    puntuacion            integer,
    resumen               text,
    mensaje_sugerido      text,
    datos                 jsonb default '{}'::jsonb,

    creado_en             timestamptz not null default now(),
    actualizado_en        timestamptz not null default now(),

    unique (tenant_id, clave)
);

create index if not exists idx_negocios_puntuacion on negocios (tenant_id, puntuacion desc);
create index if not exists idx_negocios_ciudad     on negocios (tenant_id, ciudad);
create index if not exists idx_negocios_cliente    on negocios (tenant_id, es_cliente);

-- ─────────────────────────────────────────────────────────────────────
-- 2. PERSONAS — decisores B2B
-- ─────────────────────────────────────────────────────────────────────
create table if not exists personas (
    id          uuid primary key default gen_random_uuid(),
    tenant_id   text not null default 'quantumhive',
    negocio_id  uuid references negocios (id) on delete set null,
    nombre      text not null,
    cargo       text,
    empresa     text,
    ciudad      text,
    email       text,
    linkedin    text,
    datos       jsonb default '{}'::jsonb,
    creado_en   timestamptz not null default now(),
    unique (tenant_id, linkedin)
);

-- ─────────────────────────────────────────────────────────────────────
-- 3. FUENTES — de dónde salió cada dato (para poder auditar)
-- ─────────────────────────────────────────────────────────────────────
create table if not exists fuentes (
    id         uuid primary key default gen_random_uuid(),
    negocio_id uuid not null references negocios (id) on delete cascade,
    tipo       text not null,   -- maps | web | instagram | facebook | linkedin
    url        text,
    datos      jsonb default '{}'::jsonb,
    creado_en  timestamptz not null default now()
);

create index if not exists idx_fuentes_negocio on fuentes (negocio_id);

-- ─────────────────────────────────────────────────────────────────────
-- 4. INVESTIGACIONES — cada búsqueda que corrimos
-- ─────────────────────────────────────────────────────────────────────
create table if not exists investigaciones (
    id         uuid primary key default gen_random_uuid(),
    tenant_id  text not null default 'quantumhive',
    tipo       text not null,   -- prospeccion | cliente | personas
    consulta   jsonb not null default '{}'::jsonb,
    resultados integer default 0,
    estado     text not null default 'lista',
    creado_en  timestamptz not null default now()
);

-- ─────────────────────────────────────────────────────────────────────
-- 5. OPORTUNIDADES — qué venderle a cada negocio
-- ─────────────────────────────────────────────────────────────────────
create table if not exists oportunidades (
    id         uuid primary key default gen_random_uuid(),
    negocio_id uuid not null references negocios (id) on delete cascade,
    tipo       text not null,   -- web | agente_ia | whatsapp | reservas | ...
    motivo     text,
    prioridad  text default 'media',
    creado_en  timestamptz not null default now()
);

create index if not exists idx_oportunidades_negocio on oportunidades (negocio_id);

-- ─────────────────────────────────────────────────────────────────────
-- 6. TAREAS — trabajos largos que corren en segundo plano
-- ─────────────────────────────────────────────────────────────────────
create table if not exists tareas (
    id             uuid primary key default gen_random_uuid(),
    tenant_id      text not null default 'quantumhive',
    tipo           text not null,   -- buscar | investigar | personas
    estado         text not null default 'pendiente',  -- pendiente|corriendo|lista|fallida
    datos          jsonb default '{}'::jsonb,
    resultado      jsonb,
    error          text,
    creado_en      timestamptz not null default now(),
    actualizado_en timestamptz not null default now()
);

create index if not exists idx_tareas_estado on tareas (tenant_id, estado, creado_en desc);

-- ─────────────────────────────────────────────────────────────────────
-- SEGURIDAD
--
-- La publishable key es pública: cualquiera que vea el panel la tiene. Sin
-- RLS, con esa key se pueden borrar todos los prospectos desde el navegador.
-- Entonces: el panel LEE con la publishable, y el backend ESCRIBE con la
-- service_role (que se saltea RLS por diseño y vive solo en el .env).
-- ─────────────────────────────────────────────────────────────────────

alter table negocios       enable row level security;
alter table personas       enable row level security;
alter table fuentes        enable row level security;
alter table investigaciones enable row level security;
alter table oportunidades  enable row level security;
alter table tareas         enable row level security;

do $$
declare t text;
begin
  foreach t in array array[
    'negocios','personas','fuentes','investigaciones','oportunidades','tareas'
  ] loop
    execute format('drop policy if exists lectura_publica on %I', t);
    execute format(
      'create policy lectura_publica on %I for select to anon, authenticated using (true)', t
    );
  end loop;
end $$;
