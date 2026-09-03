"""Generador del Dashboard Web Interactivo de Inteligencia Comercial."""

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="es" class="h-full bg-slate-950 text-slate-100">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Centro de Inteligencia Comercial — QuantumHive</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: {
              50: '#eef2ff',
              100: '#e0e7ff',
              400: '#818cf8',
              500: '#6366f1',
              600: '#4f46e5',
              700: '#4338ca',
              900: '#312e81',
            }
          }
        }
      }
    }
  </script>
  <style>
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #0f172a; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #475569; }
  </style>
</head>
<body class="h-full flex flex-col font-sans antialiased overflow-hidden">

  <!-- TOPBAR -->
  <header class="bg-slate-900/80 backdrop-blur border-b border-slate-800 px-6 py-3 flex items-center justify-between z-20">
    <div class="flex items-center space-x-3">
      <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-cyan-500 flex items-center justify-center font-bold text-white shadow-lg shadow-brand-500/20">
        <i class="fa-solid fa-cube text-lg"></i>
      </div>
      <div>
        <h1 class="font-bold text-base tracking-tight text-white flex items-center gap-2">
          QuantumHive
          <span class="text-xs font-medium px-2 py-0.5 rounded-full bg-brand-500/20 text-brand-400 border border-brand-500/30">Inteligencia Comercial</span>
        </h1>
        <p class="text-xs text-slate-400">Motor de Prospección, Perfilador & Cazador de Créditos</p>
      </div>
    </div>

    <!-- STATUS INDICATORS -->
    <div class="flex items-center gap-4 text-xs">
      <div id="status-ia" class="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800 border border-slate-700 text-slate-300">
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        <span>IA: <strong id="ia-provider" class="text-slate-200">OpenAI</strong></span>
      </div>
      <div id="status-db" class="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800 border border-slate-700 text-slate-300">
        <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
        <span>Supabase: <strong id="db-status" class="text-slate-200">Conectado</strong></span>
      </div>
    </div>
  </header>

  <!-- MAIN WRAPPER -->
  <div class="flex-1 flex overflow-hidden">
    <!-- SIDEBAR NAVIGATION -->
    <aside class="w-64 bg-slate-900 border-r border-slate-800 flex flex-col p-4 space-y-2 select-none">
      <div class="text-[11px] font-semibold uppercase tracking-wider text-slate-400 px-3 pt-1 pb-1">Módulos</div>
      
      <button onclick="cambiarTab('recursos')" id="nav-recursos" class="tab-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all bg-brand-600 text-white shadow-lg shadow-brand-600/20">
        <i class="fa-solid fa-gift text-brand-300 w-5 text-center"></i>
        <span>Cazador de Recursos</span>
        <span class="ml-auto text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-1.5 py-0.5 rounded font-mono font-bold">NUEVO</span>
      </button>

      <button onclick="cambiarTab('clientes')" id="nav-clientes" class="tab-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-all">
        <i class="fa-solid fa-magnifying-glass-location text-slate-400 w-5 text-center"></i>
        <span>Buscador de Clientes</span>
      </button>

      <button onclick="cambiarTab('investigar')" id="nav-investigar" class="tab-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-all">
        <i class="fa-solid fa-building-circle-check text-slate-400 w-5 text-center"></i>
        <span>Investigar Negocio</span>
      </button>

      <button onclick="cambiarTab('personas')" id="nav-personas" class="tab-btn w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-all">
        <i class="fa-brands fa-linkedin text-slate-400 w-5 text-center"></i>
        <span>Decisores B2B</span>
      </button>

      <div class="mt-auto pt-4 border-t border-slate-800 text-xs text-slate-400">
        <div class="flex items-center justify-between text-[11px] mb-1">
          <span>Token de Autorización:</span>
        </div>
        <input type="password" id="input-token" placeholder="Bearer token (opcional en local)" class="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-brand-500">
        <p class="mt-1.5 text-[10px] leading-relaxed text-slate-500">El catálogo es público. El token sólo se necesita para buscar, investigar, cazar en vivo o generar postulaciones.</p>
      </div>
    </aside>

    <!-- CONTENT AREA -->
    <main class="flex-1 overflow-y-auto p-6 bg-slate-950">
      
      <!-- ════════════ TAB 1: CAZADOR DE RECURSOS & CRÉDITOS ════════════ -->
      <section id="tab-recursos" class="space-y-6">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/60 p-5 rounded-2xl border border-slate-800">
          <div>
            <h2 class="text-xl font-bold text-white flex items-center gap-2">
              <i class="fa-solid fa-gift text-brand-400"></i>
              Cazador de Créditos Cloud, Developers & Beneficios
            </h2>
            <p class="text-sm text-slate-400 mt-1">
              Catálogo de subsidios, créditos de cómputo/IA y beneficios educativos con correo <code>universitario</code> o <code>@corporativo</code>.
            </p>
          </div>

          <!-- PERFIL POSTULANTE TOGGLES -->
          <div class="flex flex-wrap items-center gap-3 bg-slate-950/80 p-2 rounded-xl border border-slate-800">
            <label class="flex items-center gap-2 text-xs text-slate-300 cursor-pointer px-2.5 py-1.5 rounded-lg hover:bg-slate-800 transition">
              <input type="checkbox" id="filtro-edu" checked onchange="cargarRecursos()" class="rounded bg-slate-900 border-slate-700 text-brand-600 focus:ring-0">
              <span class="flex items-center gap-1.5"><i class="fa-solid fa-graduation-cap text-amber-400"></i> Correo universitario</span>
            </label>
            <label class="flex items-center gap-2 text-xs text-slate-300 cursor-pointer px-2.5 py-1.5 rounded-lg hover:bg-slate-800 transition">
              <input type="checkbox" id="filtro-corp" checked onchange="cargarRecursos()" class="rounded bg-slate-900 border-slate-700 text-brand-600 focus:ring-0">
              <span class="flex items-center gap-1.5"><i class="fa-solid fa-briefcase text-cyan-400"></i> Correo @Corp</span>
            </label>
          </div>
        </div>

        <!-- FILTROS Y BÚSQUEDA -->
        <div class="flex flex-wrap items-center gap-3">
          <div class="flex-1 min-w-[240px] relative">
            <i class="fa-solid fa-search absolute left-3.5 top-3 text-slate-500 text-xs"></i>
            <input type="text" id="busqueda-recurso" oninput="cargarRecursos()" placeholder="Buscar por tecnología, proveedor (AWS, Azure, NVIDIA, GitHub)..." class="w-full bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500">
          </div>

          <div class="flex items-center gap-2 overflow-x-auto pb-1" id="cat-chips">
            <button onclick="filtrarCategoria(null)" class="cat-chip px-3 py-1.5 rounded-lg text-xs font-medium bg-brand-600 text-white">Todos</button>
            <button onclick="filtrarCategoria('cloud')" class="cat-chip px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-900 border border-slate-800 text-slate-400 hover:text-white">Créditos Cloud</button>
            <button onclick="filtrarCategoria('ai_startup')" class="cat-chip px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-900 border border-slate-800 text-slate-400 hover:text-white">IA & Startups</button>
            <button onclick="filtrarCategoria('educativo')" class="cat-chip px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-900 border border-slate-800 text-slate-400 hover:text-white">Educativo</button>
            <button onclick="filtrarCategoria('dev_tools')" class="cat-chip px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-900 border border-slate-800 text-slate-400 hover:text-white">Dev Tools</button>
            <button onclick="filtrarCategoria('saas_perks')" class="cat-chip px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-900 border border-slate-800 text-slate-400 hover:text-white">SaaS Perks</button>
          </div>

          <button onclick="abrirModalCazarWeb()" class="px-3.5 py-2 rounded-xl text-xs font-semibold bg-gradient-to-r from-emerald-600 to-teal-600 text-white hover:opacity-95 flex items-center gap-2 shadow-lg shadow-emerald-900/20">
            <i class="fa-solid fa-radar"></i> Cazar en la Web
          </button>
        </div>

        <!-- RECURSOS GRID -->
        <div id="grid-recursos" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          <!-- Renderizado dinámico -->
        </div>
      </section>

      <!-- ════════════ TAB 2: BUSCADOR DE CLIENTES ════════════ -->
      <section id="tab-clientes" class="space-y-6 hidden">
        <div class="bg-slate-900/60 p-5 rounded-2xl border border-slate-800">
          <h2 class="text-xl font-bold text-white flex items-center gap-2">
            <i class="fa-solid fa-magnifying-glass-location text-brand-400"></i>
            Buscador de Clientes en Google Maps
          </h2>
          <p class="text-sm text-slate-400 mt-1">Rastrea negocios por rubro y ciudad, extrae contactos, analiza webs y calcula scoring comercial.</p>

          <form id="form-buscar-clientes" onsubmit="ejecutarBusquedaClientes(event)" class="mt-4 grid grid-cols-1 md:grid-cols-4 gap-3">
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1">Rubro / Categoría</label>
              <input type="text" id="buscar-rubro" required placeholder="ej: barberías, clínicas, abogados" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-brand-500">
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1">Ciudad / Región</label>
              <input type="text" id="buscar-ciudad" required placeholder="ej: Buenos Aires, Madrid" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-brand-500">
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1">Cantidad</label>
              <select id="buscar-cantidad" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-brand-500">
                <option value="5">5 negocios (prueba rápida)</option>
                <option value="10" selected>10 negocios</option>
                <option value="20">20 negocios</option>
                <option value="30">30 negocios</option>
              </select>
            </div>
            <div class="flex items-end">
              <button type="submit" id="btn-buscar-clientes" class="w-full py-2 px-4 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-medium text-sm flex items-center justify-center gap-2 transition shadow-lg shadow-brand-600/30">
                <i class="fa-solid fa-play"></i> Iniciar Prospección
              </button>
            </div>
          </form>
        </div>

        <!-- RESULTADOS BUSCADOR -->
        <div id="contenedor-resultados-clientes" class="space-y-4">
          <div id="estado-busqueda" class="hidden p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="animate-spin text-brand-400"><i class="fa-solid fa-circle-notch text-lg"></i></div>
              <span id="texto-estado-busqueda" class="text-sm text-slate-300">Buscando negocios en segundo plano...</span>
            </div>
            <span id="timer-busqueda" class="text-xs font-mono text-slate-500">0s</span>
          </div>

          <div id="tabla-clientes-contenedor" class="hidden bg-slate-900 rounded-2xl border border-slate-800 overflow-hidden">
            <div class="p-4 border-b border-slate-800 flex items-center justify-between">
              <h3 class="font-semibold text-sm text-white">Negocios Encontrados (<span id="total-clientes-count">0</span>)</h3>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-left text-xs text-slate-300">
                <thead class="bg-slate-950/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
                  <tr>
                    <th class="px-4 py-3">Puntaje</th>
                    <th class="px-4 py-3">Negocio</th>
                    <th class="px-4 py-3">Contacto</th>
                    <th class="px-4 py-3">Web / Tech</th>
                    <th class="px-4 py-3">Oportunidad Comercial</th>
                    <th class="px-4 py-3 text-right">Acción</th>
                  </tr>
                </thead>
                <tbody id="tbody-clientes" class="divide-y divide-slate-800/60">
                  <!-- Filas renderizadas -->
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      <!-- ════════════ TAB 3: INVESTIGAR NEGOCIO / ONBOARDING ════════════ -->
      <section id="tab-investigar" class="space-y-6 hidden">
        <div class="bg-slate-900/60 p-5 rounded-2xl border border-slate-800">
          <h2 class="text-xl font-bold text-white flex items-center gap-2">
            <i class="fa-solid fa-building-circle-check text-brand-400"></i>
            Perfilador de Cliente & Onboarding
          </h2>
          <p class="text-sm text-slate-400 mt-1">Extrae ficha completa, servicios, precios, FAQs, logo y paleta de colores para la Fábrica de Webs / Agentes.</p>

          <form id="form-investigar" onsubmit="ejecutarInvestigacion(event)" class="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1">Nombre del Negocio / Cliente *</label>
              <input type="text" id="inv-nombre" required placeholder="ej: Barbería El Zorro" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-brand-500">
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1">Sitio Web (opcional)</label>
              <input type="url" id="inv-web" placeholder="https://ejemplo.com" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-brand-500">
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1">Instagram (opcional)</label>
              <input type="text" id="inv-instagram" placeholder="@usuario o URL" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-brand-500">
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1">Google Maps URL (opcional)</label>
              <input type="url" id="inv-maps" placeholder="https://maps.app.goo.gl/..." class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-brand-500">
            </div>
            <div class="md:col-span-2 flex justify-end">
              <button type="submit" id="btn-investigar" class="py-2.5 px-6 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-medium text-sm flex items-center gap-2 transition shadow-lg shadow-brand-600/30">
                <i class="fa-solid fa-microscope"></i> Investigar & Extraer Identidad
              </button>
            </div>
          </form>
        </div>

        <div id="resultado-investigacion" class="hidden space-y-6">
          <!-- Tarjeta de Identidad Visual -->
          <div class="bg-slate-900 p-5 rounded-2xl border border-slate-800 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="flex items-center gap-4">
              <div id="ficha-logo-preview" class="w-20 h-20 rounded-2xl bg-slate-950 border border-slate-800 flex items-center justify-center overflow-hidden p-2">
                <i class="fa-regular fa-image text-slate-600 text-2xl"></i>
              </div>
              <div>
                <h3 id="ficha-nombre" class="font-bold text-lg text-white">Nombre Negocio</h3>
                <span id="ficha-categoria" class="text-xs text-brand-400 font-medium">Categoría</span>
                <p id="ficha-direccion" class="text-xs text-slate-400 mt-1">Dirección</p>
              </div>
            </div>

            <!-- Paleta de Colores -->
            <div class="md:col-span-2 bg-slate-950 p-4 rounded-xl border border-slate-800 flex flex-col justify-center">
              <span class="text-xs font-semibold text-slate-400 mb-2">Paleta de Colores Dominantes:</span>
              <div id="ficha-paleta" class="flex items-center gap-3">
                <!-- Colores -->
              </div>
            </div>
          </div>

          <!-- Servicios y Precios -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-slate-900 p-5 rounded-2xl border border-slate-800">
              <h4 class="font-semibold text-sm text-white mb-3 flex items-center gap-2">
                <i class="fa-solid fa-list-check text-brand-400"></i> Servicios Detectados
              </h4>
              <ul id="ficha-servicios" class="space-y-1.5 text-xs text-slate-300"></ul>
            </div>

            <div class="bg-slate-900 p-5 rounded-2xl border border-slate-800">
              <h4 class="font-semibold text-sm text-white mb-3 flex items-center gap-2">
                <i class="fa-solid fa-tags text-emerald-400"></i> Precios Detectados
              </h4>
              <ul id="ficha-precios" class="space-y-1.5 text-xs text-slate-300"></ul>
            </div>
          </div>
        </div>
      </section>

      <!-- ════════════ TAB 4: DECISORES B2B ════════════ -->
      <section id="tab-personas" class="space-y-6 hidden">
        <div class="bg-slate-900/60 p-5 rounded-2xl border border-slate-800">
          <h2 class="text-xl font-bold text-white flex items-center gap-2">
            <i class="fa-brands fa-linkedin text-cyan-400"></i>
            Decisores B2B & Perfiles de LinkedIn
          </h2>
          <p class="text-sm text-slate-400 mt-1">Encuentra directores, CEOs y dueños indexados públicamente sin riesgo de bloqueo de scraping.</p>

          <form id="form-personas" onsubmit="ejecutarBusquedaPersonas(event)" class="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3">
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1">Rubro de la Empresa</label>
              <input type="text" id="per-rubro" required placeholder="ej: software, logística, fintech" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-brand-500">
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1">País o Ciudad</label>
              <input type="text" id="per-ciudad" placeholder="ej: Argentina, México, España" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-brand-500">
            </div>
            <div class="flex items-end">
              <button type="submit" id="btn-personas" class="w-full py-2 px-4 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-medium text-sm flex items-center justify-center gap-2 transition shadow-lg shadow-brand-600/30">
                <i class="fa-solid fa-user-tie"></i> Buscar Decisores
              </button>
            </div>
          </form>
        </div>

        <div id="tabla-personas-contenedor" class="hidden bg-slate-900 rounded-2xl border border-slate-800 overflow-hidden">
          <div class="p-4 border-b border-slate-800">
            <h3 class="font-semibold text-sm text-white">Decisores Encontrados (<span id="total-personas-count">0</span>)</h3>
          </div>
          <div id="lista-personas" class="divide-y divide-slate-800/60 p-2"></div>
        </div>
      </section>

    </main>
  </div>

  <!-- ════════════ MODAL: ASISTENTE DE POSTULACIÓN IA ════════════ -->
  <div id="modal-postulacion" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 hidden">
    <div class="bg-slate-900 border border-slate-800 w-full max-w-2xl rounded-2xl shadow-2xl flex flex-col max-h-[90vh] overflow-hidden">
      <div class="p-5 border-b border-slate-800 flex items-center justify-between">
        <div>
          <h3 class="font-bold text-base text-white flex items-center gap-2">
            <i class="fa-solid fa-wand-magic-sparkles text-brand-400"></i>
            Asistente de Postulación: <span id="modal-recurso-titulo" class="text-brand-300">Programa</span>
          </h3>
          <p class="text-xs text-slate-400 mt-0.5">Genera pitch, arquitectura y argumentos técnicos para ser aprobado al 100%.</p>
        </div>
        <button onclick="cerrarModalPostulacion()" class="text-slate-400 hover:text-white"><i class="fa-solid fa-xmark text-lg"></i></button>
      </div>

      <div class="p-6 overflow-y-auto space-y-4">
        <!-- Formulario inputs -->
        <div id="modal-form-inputs" class="space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1">Nombre del Proyecto *</label>
              <input type="text" id="post-nombre" placeholder="ej: QuantumHive AI" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:border-brand-500">
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1">Correo para Postular *</label>
              <input type="email" id="post-correo" placeholder="ej: sergio@universidad.edu o info@miempresa.com" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:border-brand-500">
            </div>
          </div>
          <div>
            <label class="block text-xs font-medium text-slate-400 mb-1">Descripción Breve de la Solución *</label>
            <textarea id="post-desc" rows="2" placeholder="ej: Plataforma de agentes inteligentes para automatización comercial y análisis de datos en tiempo real..." class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:border-brand-500"></textarea>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1">Tipo de Postulante</label>
              <select id="post-tipo" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:border-brand-500">
                <option value="startup">Startup / Empresa (Correo Corporativo)</option>
                <option value="estudiante">Estudiante / Académico (Correo universitario)</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-1">Stack Tecnológico</label>
              <input type="text" id="post-stack" value="Python, FastAPI, IA, Docker, Cloud" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:border-brand-500">
            </div>
          </div>

          <button onclick="generarPitchIA()" id="btn-generar-pitch" class="w-full py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-medium text-xs flex items-center justify-center gap-2 transition shadow-lg shadow-brand-600/30">
            <i class="fa-solid fa-bolt"></i> Generar Respuestas con IA
          </button>
        </div>

        <!-- Respuestas generadas -->
        <div id="modal-respuestas-ia" class="hidden space-y-4 pt-4 border-t border-slate-800">
          <div id="origen-postulacion" class="text-xs p-3 rounded-xl border"></div>
          <div>
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs font-bold text-slate-300">1. Pitch del Proyecto (Pegar en descripción):</span>
              <button onclick="copiarTexto('pitch-res')" class="text-[11px] text-brand-400 hover:text-brand-300 flex items-center gap-1"><i class="fa-regular fa-copy"></i> Copiar</button>
            </div>
            <p id="pitch-res" class="text-xs bg-slate-950 p-3 rounded-xl border border-slate-800 text-slate-300 leading-relaxed font-mono whitespace-pre-wrap"></p>
          </div>

          <div>
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs font-bold text-slate-300">2. Caso de Uso de Créditos & Cómputo:</span>
              <button onclick="copiarTexto('creditos-res')" class="text-[11px] text-brand-400 hover:text-brand-300 flex items-center gap-1"><i class="fa-regular fa-copy"></i> Copiar</button>
            </div>
            <p id="creditos-res" class="text-xs bg-slate-950 p-3 rounded-xl border border-slate-800 text-slate-300 leading-relaxed font-mono whitespace-pre-wrap"></p>
          </div>

          <div>
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs font-bold text-slate-300">3. Arquitectura Técnica Recomendada:</span>
              <button onclick="copiarTexto('arq-res')" class="text-[11px] text-brand-400 hover:text-brand-300 flex items-center gap-1"><i class="fa-regular fa-copy"></i> Copiar</button>
            </div>
            <p id="arq-res" class="text-xs bg-slate-950 p-3 rounded-xl border border-slate-800 text-slate-300 leading-relaxed font-mono whitespace-pre-wrap"></p>
          </div>

          <div class="bg-emerald-950/30 p-3 rounded-xl border border-emerald-800/40">
            <span class="text-xs font-bold text-emerald-300 mb-1 block">Checklist antes de enviar:</span>
            <ul id="checklist-res" class="space-y-1 text-xs text-slate-300 list-disc list-inside"></ul>
          </div>

          <a id="link-oficial-postular" target="_blank" href="#" class="block w-full text-center py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-lg shadow-emerald-600/30">
            <i class="fa-solid fa-arrow-up-right-from-square mr-1"></i> Ir al Formulario Oficial de Postulación
          </a>
        </div>
      </div>
    </div>
  </div>

  <!-- JAVASCRIPT FRONTEND LOGIC -->
  <script>
    let categoriaActiva = null;
    let recursoActualSeleccionado = null;

    function getHeaders() {
      const token = document.getElementById('input-token').value.trim();
      const headers = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;
      return headers;
    }

    function cambiarTab(tab) {
      document.querySelectorAll('section[id^="tab-"]').forEach(s => s.classList.add('hidden'));
      document.getElementById(`tab-${tab}`).classList.remove('hidden');

      document.querySelectorAll('.tab-btn').forEach(b => {
        b.classList.remove('bg-brand-600', 'text-white', 'shadow-lg');
        b.classList.add('text-slate-400');
      });
      const activeBtn = document.getElementById(`nav-${tab}`);
      activeBtn.classList.add('bg-brand-600', 'text-white', 'shadow-lg', 'shadow-brand-600/20');
      activeBtn.classList.remove('text-slate-400');
    }

    let iaDisponible = false;

    async function verificarSalud() {
      try {
        const res = await fetch('/salud');
        const data = await res.json();
        iaDisponible = Boolean(data.ia_configurada);
        const statusIa = document.getElementById('status-ia');
        statusIa.querySelector('span').className = `w-2 h-2 rounded-full ${iaDisponible ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`;
        document.getElementById('ia-provider').innerText = iaDisponible
          ? (data.proveedor_ia || 'IA').toUpperCase()
          : 'Sin configurar';
        document.getElementById('db-status').innerText = data.supabase_configurado ? 'Conectado' : 'Local';
      } catch (e) {
        console.error("No se pudo verificar salud:", e);
      }
    }

    async function cargarRecursos() {
      const tieneEdu = document.getElementById('filtro-edu').checked;
      const tieneCorp = document.getElementById('filtro-corp').checked;
      const texto = document.getElementById('busqueda-recurso').value;

      const params = new URLSearchParams();
      if (categoriaActiva) params.append('categoria', categoriaActiva);
      params.append('tiene_correo_estudiante', tieneEdu);
      params.append('tiene_correo_corporativo', tieneCorp);
      if (texto) params.append('texto_busqueda', texto);

      try {
        const res = await fetch(`/api/recursos?${params.toString()}`, { headers: getHeaders() });
        if (!res.ok) {
          const error = await res.json().catch(() => ({}));
          throw new Error(error.detail || `No se pudo cargar el catálogo (${res.status})`);
        }
        const recursos = await res.json();
        renderizarRecursos(recursos);
      } catch (e) {
        console.error("Error al cargar recursos:", e);
        const grid = document.getElementById('grid-recursos');
        grid.innerHTML = `<div class="col-span-3 rounded-2xl border border-amber-800/40 bg-amber-950/30 p-6 text-center text-sm text-amber-200"><i class="fa-solid fa-triangle-exclamation mr-2"></i>${e.message}</div>`;
      }
    }

    function filtrarCategoria(cat) {
      categoriaActiva = cat;
      document.querySelectorAll('.cat-chip').forEach(c => {
        c.classList.remove('bg-brand-600', 'text-white');
        c.classList.add('bg-slate-900', 'text-slate-400');
      });
      event.target.classList.add('bg-brand-600', 'text-white');
      event.target.classList.remove('bg-slate-900', 'text-slate-400');
      cargarRecursos();
    }

    function renderizarRecursos(recursos) {
      const grid = document.getElementById('grid-recursos');
      grid.innerHTML = '';

      if (!recursos || recursos.length === 0) {
        grid.innerHTML = `<div class="col-span-3 text-center py-12 text-slate-500 text-sm">No se encontraron programas con esos filtros.</div>`;
        return;
      }

      recursos.forEach(r => {
        const card = document.createElement('div');
        card.className = 'bg-slate-900 rounded-2xl border border-slate-800 p-5 flex flex-col justify-between hover:border-slate-700 transition space-y-4';

        let badgeCorreo = '';
        if (r.correo_requerido === 'estudiante') {
          badgeCorreo = '<span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30"><i class="fa-solid fa-graduation-cap mr-1"></i> Correo universitario</span>';
        } else if (r.correo_requerido === 'corporativo') {
          badgeCorreo = '<span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30"><i class="fa-solid fa-briefcase mr-1"></i> Correo @Corp</span>';
        } else {
          badgeCorreo = '<span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">Cualquier correo</span>';
        }

        const montoStr = r.monto_estimado_usd ? `$${r.monto_estimado_usd.toLocaleString()} USD` : 'Varía';

        card.innerHTML = `
          <div>
            <div class="flex items-start justify-between gap-2 mb-2">
              <span class="text-xs font-semibold text-brand-400 uppercase tracking-wider">${r.proveedor}</span>
              ${badgeCorreo}
            </div>
            <h3 class="font-bold text-base text-white leading-snug">${r.nombre}</h3>
            <div class="mt-2 text-xs font-medium text-emerald-400 bg-emerald-950/40 border border-emerald-800/40 p-2 rounded-xl">
              <i class="fa-solid fa-coins mr-1"></i> ${r.beneficio_principal}
            </div>
            <p class="text-xs text-slate-400 mt-3 leading-relaxed line-clamp-3">${r.descripcion}</p>
          </div>

          <div class="pt-3 border-t border-slate-800/80 flex items-center justify-between gap-2">
            <a href="${r.url_oficial}" target="_blank" class="text-xs text-slate-400 hover:text-white flex items-center gap-1">
              Oficial <i class="fa-solid fa-arrow-up-right-from-square text-[10px]"></i>
            </a>
            <button onclick="abrirModalPostulacion('${r.id}')" class="px-3 py-1.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-medium text-xs flex items-center gap-1.5 shadow-md shadow-brand-600/20">
              <i class="fa-solid fa-wand-magic-sparkles"></i> Postular con IA
            </button>
          </div>
        `;
        grid.appendChild(card);
      });
    }

    async function abrirModalPostulacion(recursoId) {
      try {
        const res = await fetch(`/api/recursos`, { headers: getHeaders() });
        if (!res.ok) {
          const error = await res.json().catch(() => ({}));
          throw new Error(error.detail || `No se pudo abrir el recurso (${res.status})`);
        }
        const list = await res.json();
        recursoActualSeleccionado = list.find(x => x.id === recursoId);
        if (!recursoActualSeleccionado) return;

        document.getElementById('modal-recurso-titulo').innerText = recursoActualSeleccionado.nombre;
        document.getElementById('link-oficial-postular').href = recursoActualSeleccionado.url_oficial;

        if (recursoActualSeleccionado.correo_requerido === 'estudiante') {
          document.getElementById('post-tipo').value = 'estudiante';
        } else {
          document.getElementById('post-tipo').value = 'startup';
        }

        document.getElementById('modal-respuestas-ia').classList.add('hidden');
        document.getElementById('modal-postulacion').classList.remove('hidden');
      } catch (e) {
        console.error(e);
      }
    }

    function cerrarModalPostulacion() {
      document.getElementById('modal-postulacion').classList.add('hidden');
    }

    async function generarPitchIA() {
      const btn = document.getElementById('btn-generar-pitch');
      const nombre = document.getElementById('post-nombre').value.trim();
      const correo = document.getElementById('post-correo').value.trim();
      const desc = document.getElementById('post-desc').value.trim();
      const tipo = document.getElementById('post-tipo').value;
      const stack = document.getElementById('post-stack').value.split(',').map(s => s.trim());

      if (!nombre || !correo || !desc) {
        alert("Por favor completa el nombre, correo y descripción del proyecto.");
        return;
      }

      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-circle-notch animate-spin"></i> Generando pitch con IA...';

      try {
        const body = {
          recurso_id: recursoActualSeleccionado.id,
          nombre_proyecto: nombre,
          descripcion_proyecto: desc,
          tipo_postulante: tipo,
          correo_a_usar: correo,
          stack_tecnologico: stack
        };

        const res = await fetch('/api/recursos/postular', {
          method: 'POST',
          headers: getHeaders(),
          body: JSON.stringify(body)
        });

        if (!res.ok) {
          const error = await res.json().catch(() => ({}));
          throw new Error(error.detail || `No se pudo generar la postulación (${res.status})`);
        }

        const data = await res.json();

        const origen = document.getElementById('origen-postulacion');
        if (data.generado_con_ia) {
          origen.className = 'text-xs p-3 rounded-xl border bg-emerald-950/30 border-emerald-800/40 text-emerald-300';
          origen.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles mr-1"></i> Generado con IA configurada.';
        } else {
          origen.className = 'text-xs p-3 rounded-xl border bg-amber-950/30 border-amber-800/40 text-amber-300';
          origen.innerHTML = '<i class="fa-solid fa-triangle-exclamation mr-1"></i> Borrador base: la IA no está configurada o falló. Revisalo antes de postular.';
        }

        document.getElementById('pitch-res').innerText = data.pitch_elevator;
        document.getElementById('creditos-res').innerText = data.caso_de_uso_creditos;
        document.getElementById('arq-res').innerText = data.arquitectura_tecnica;

        const checklistUl = document.getElementById('checklist-res');
        checklistUl.innerHTML = '';
        (data.checklist_antes_de_enviar || []).forEach(item => {
          const li = document.createElement('li');
          li.innerText = item;
          checklistUl.appendChild(li);
        });

        document.getElementById('modal-respuestas-ia').classList.remove('hidden');
      } catch (e) {
        alert("Error al generar postulación: " + e.message);
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-bolt"></i> Regenerar Respuestas';
      }
    }

    function copiarTexto(elementId) {
      const text = document.getElementById(elementId).innerText;
      navigator.clipboard.writeText(text);
      alert("¡Copiado al portapapeles listo para pegar!");
    }

    // ════════ BUSCADOR CLIENTES ════════
    let searchTimer = null;
    let elapsedSeconds = 0;

    async function ejecutarBusquedaClientes(e) {
      e.preventDefault();
      const rubro = document.getElementById('buscar-rubro').value.trim();
      const ciudad = document.getElementById('buscar-ciudad').value.trim();
      const cantidad = parseInt(document.getElementById('buscar-cantidad').value);

      const btn = document.getElementById('btn-buscar-clientes');
      btn.disabled = true;
      document.getElementById('estado-busqueda').classList.remove('hidden');
      document.getElementById('tabla-clientes-contenedor').classList.add('hidden');

      elapsedSeconds = 0;
      searchTimer = setInterval(() => {
        elapsedSeconds++;
        document.getElementById('timer-busqueda').innerText = `${elapsedSeconds}s`;
      }, 1000);

      try {
        const res = await fetch('/buscar', {
          method: 'POST',
          headers: getHeaders(),
          body: JSON.stringify({ rubro, ciudad, cantidad, analizar: true, guardar: true })
        });
        const data = await res.json();
        const tareaId = data.tarea_id;
        pollTarea(tareaId);
      } catch (err) {
        alert("Error al iniciar búsqueda: " + err.message);
        clearInterval(searchTimer);
        btn.disabled = false;
        document.getElementById('estado-busqueda').classList.add('hidden');
      }
    }

    async function pollTarea(tareaId) {
      try {
        const res = await fetch(`/tareas/${tareaId}`, { headers: getHeaders() });
        const tarea = await res.json();

        if (tarea.estado === 'lista') {
          clearInterval(searchTimer);
          document.getElementById('estado-busqueda').classList.add('hidden');
          document.getElementById('btn-buscar-clientes').disabled = false;
          renderizarTablaClientes(tarea.resultado.negocios);
        } else if (tarea.estado === 'fallida') {
          clearInterval(searchTimer);
          alert("La búsqueda falló: " + (tarea.error || 'Error desconocido'));
          document.getElementById('estado-busqueda').classList.add('hidden');
          document.getElementById('btn-buscar-clientes').disabled = false;
        } else {
          setTimeout(() => pollTarea(tareaId), 2500);
        }
      } catch (e) {
        console.error(e);
        setTimeout(() => pollTarea(tareaId), 3000);
      }
    }

    function renderizarTablaClientes(negocios) {
      const tbody = document.getElementById('tbody-clientes');
      tbody.innerHTML = '';
      document.getElementById('total-clientes-count').innerText = negocios.length;

      negocios.forEach(item => {
        const n = item.negocio;
        const a = item.analisis;
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-800/40 transition';

        const puntuacion = a ? a.puntuacion : 0;
        let scoreClass = 'bg-slate-800 text-slate-300';
        if (puntuacion >= 75) scoreClass = 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30';
        else if (puntuacion >= 50) scoreClass = 'bg-amber-500/20 text-amber-300 border border-amber-500/30';

        tr.innerHTML = `
          <td class="px-4 py-3">
            <span class="px-2.5 py-1 rounded-lg text-xs font-bold font-mono ${scoreClass}">${puntuacion}/100</span>
          </td>
          <td class="px-4 py-3">
            <div class="font-bold text-white text-xs">${n.nombre}</div>
            <div class="text-[11px] text-slate-400">${n.categoria || 'Sin rubro'} · ${n.direccion || 'Sin dir'}</div>
          </td>
          <td class="px-4 py-3">
            <div class="text-xs text-slate-300">${n.telefono || '—'}</div>
            <div class="text-[11px] text-slate-500">${n.email || 'Sin email'}</div>
          </td>
          <td class="px-4 py-3">
            ${n.web ? `<a href="${n.web}" target="_blank" class="text-brand-400 hover:underline text-xs flex items-center gap-1">${n.web.substring(0, 20)}... <i class="fa-solid fa-external-link text-[10px]"></i></a>` : '<span class="text-amber-400 text-xs">Sin web</span>'}
            <div class="text-[10px] text-slate-400">${(n.tecnologias || []).join(', ') || 'N/A'}</div>
          </td>
          <td class="px-4 py-3">
            <div class="text-xs text-slate-300">${(a && a.oferta_recomendada) ? a.oferta_recomendada.slice(0, 2).join(', ') : '—'}</div>
            <div class="text-[10px] text-slate-400">${(a && a.problemas) ? a.problemas.slice(0, 1).join(', ') : ''}</div>
          </td>
          <td class="px-4 py-3 text-right">
            ${(a && a.mensaje_sugerido) ? `<button onclick="alert('${a.mensaje_sugerido.replace(/'/g, "\\'")}')" class="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-xs text-brand-300">Ver Mensaje</button>` : '—'}
          </td>
        `;
        tbody.appendChild(tr);
      });

      document.getElementById('tabla-clientes-contenedor').classList.remove('hidden');
    }

    // ════════ INVESTIGACIÓN / ONBOARDING ════════
    async function ejecutarInvestigacion(e) {
      e.preventDefault();
      const nombre = document.getElementById('inv-nombre').value.trim();
      const web = document.getElementById('inv-web').value.trim() || null;
      const instagram = document.getElementById('inv-instagram').value.trim() || null;
      const maps = document.getElementById('inv-maps').value.trim() || null;

      const btn = document.getElementById('btn-investigar');
      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-circle-notch animate-spin"></i> Investigando con scraping & IA...';

      try {
        const res = await fetch('/clientes/investigar', {
          method: 'POST',
          headers: getHeaders(),
          body: JSON.stringify({ nombre, web, instagram, url_maps: maps })
        });
        const data = await res.json();

        document.getElementById('ficha-nombre').innerText = data.negocio.nombre;
        document.getElementById('ficha-categoria').innerText = data.negocio.categoria || 'Negocio';
        document.getElementById('ficha-direccion').innerText = data.negocio.direccion || 'Sin dirección';

        const logoDiv = document.getElementById('ficha-logo-preview');
        if (data.marca && data.marca.logo_url) {
          logoDiv.innerHTML = `<img src="${data.marca.logo_url}" class="w-full h-full object-contain">`;
        } else {
          logoDiv.innerHTML = `<i class="fa-regular fa-image text-slate-600 text-2xl"></i>`;
        }

        const paletaDiv = document.getElementById('ficha-paleta');
        paletaDiv.innerHTML = '';
        (data.marca.colores || []).forEach(color => {
          const cBox = document.createElement('div');
          cBox.className = 'flex flex-col items-center gap-1';
          cBox.innerHTML = `
            <div class="w-8 h-8 rounded-lg border border-white/20 shadow-md" style="background-color: ${color}"></div>
            <span class="text-[10px] font-mono text-slate-400">${color}</span>
          `;
          paletaDiv.appendChild(cBox);
        });

        const servUl = document.getElementById('ficha-servicios');
        servUl.innerHTML = '';
        (data.servicios || []).forEach(s => {
          const li = document.createElement('li');
          li.innerHTML = `<i class="fa-solid fa-check text-emerald-400 mr-1.5"></i> ${s}`;
          servUl.appendChild(li);
        });
        if (!data.servicios || data.servicios.length === 0) {
          servUl.innerHTML = `<li class="text-amber-300"><i class="fa-solid fa-circle-info mr-1.5"></i>${iaDisponible ? 'No se encontraron servicios explícitos en el contenido público.' : 'No disponibles: configurá una clave de IA válida.'}</li>`;
        }

        const precUl = document.getElementById('ficha-precios');
        precUl.innerHTML = '';
        (data.precios || []).forEach(p => {
          const li = document.createElement('li');
          li.innerHTML = `<i class="fa-solid fa-tag text-emerald-400 mr-1.5"></i> ${p}`;
          precUl.appendChild(li);
        });
        if (!data.precios || data.precios.length === 0) {
          precUl.innerHTML = `<li class="text-amber-300"><i class="fa-solid fa-circle-info mr-1.5"></i>${iaDisponible ? 'No se encontraron precios públicos.' : 'No disponibles: configurá una clave de IA válida.'}</li>`;
        }

        document.getElementById('resultado-investigacion').classList.remove('hidden');
      } catch (err) {
        alert("Error al investigar: " + err.message);
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-microscope"></i> Investigar & Extraer Identidad';
      }
    }

    // ════════ DECISORES B2B ════════
    async function ejecutarBusquedaPersonas(e) {
      e.preventDefault();
      const rubro = document.getElementById('per-rubro').value.trim();
      const ciudad = document.getElementById('per-ciudad').value.trim() || null;

      const btn = document.getElementById('btn-personas');
      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-circle-notch animate-spin"></i> Buscando perfiles...';

      try {
        const res = await fetch('/personas', {
          method: 'POST',
          headers: getHeaders(),
          body: JSON.stringify({ rubro, ciudad, cantidad: 15 })
        });
        const personas = await res.json();
        renderizarPersonas(personas);
      } catch (err) {
        alert("Error: " + err.message);
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-user-tie"></i> Buscar Decisores';
      }
    }

    function renderizarPersonas(personas) {
      const cont = document.getElementById('lista-personas');
      cont.innerHTML = '';
      document.getElementById('total-personas-count').innerText = personas.length;

      personas.forEach(p => {
        const row = document.createElement('div');
        row.className = 'p-3 flex items-center justify-between hover:bg-slate-800/40 rounded-xl transition';
        row.innerHTML = `
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-full bg-cyan-950 border border-cyan-800 flex items-center justify-center text-cyan-400">
              <i class="fa-solid fa-user"></i>
            </div>
            <div>
              <h4 class="font-bold text-xs text-white">${p.nombre}</h4>
              <p class="text-[11px] text-slate-400">${p.cargo || 'Directivo'} en <span class="text-brand-400">${p.empresa || 'Empresa'}</span></p>
            </div>
          </div>
          <a href="${p.linkedin}" target="_blank" class="px-3 py-1 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-medium flex items-center gap-1.5">
            <i class="fa-brands fa-linkedin"></i> Ver Perfil
          </a>
        `;
        cont.appendChild(row);
      });

      document.getElementById('tabla-personas-contenedor').classList.remove('hidden');
    }

    // ════════ CAZADOR WEB EN VIVO ════════
    async function abrirModalCazarWeb() {
      const termino = prompt("¿Qué querés buscar? (ej: creditos cloud startups Argentina 2026):", "creditos cloud startups 2026");
      if (!termino) return;

      const btn = event.target.closest('button');
      const originalHTML = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-circle-notch animate-spin"></i> Cazando...';

      try {
        const params = new URLSearchParams({ termino, cantidad: '10' });
        const res = await fetch(`/api/recursos/cazar-web?${params.toString()}`, {
          method: 'POST',
          headers: getHeaders(),
        });
        if (!res.ok) {
          const error = await res.json().catch(() => ({}));
          throw new Error(error.detail || `No se pudo ejecutar la búsqueda web (${res.status})`);
        }
        const nuevos = await res.json();

        if (!nuevos || nuevos.length === 0) {
          alert("No se encontraron resultados para esa búsqueda. Probá con otros términos.");
          return;
        }

        // Agregar los resultados al grid existente
        const grid = document.getElementById('grid-recursos');

        // Separador visual
        const sep = document.createElement('div');
        sep.className = 'col-span-full flex items-center gap-3 py-2';
        sep.innerHTML = `<div class="h-px flex-1 bg-emerald-800/40"></div><span class="text-xs font-bold text-emerald-400"><i class="fa-solid fa-radar mr-1"></i> ${nuevos.length} resultado(s) encontrados en la web</span><div class="h-px flex-1 bg-emerald-800/40"></div>`;
        grid.appendChild(sep);

        renderizarRecursos(nuevos);
      } catch (e) {
        alert("Error al buscar en la web: " + e.message);
      } finally {
        btn.disabled = false;
        btn.innerHTML = originalHTML;
      }
    }

    // Init
    window.addEventListener('DOMContentLoaded', () => {
      verificarSalud();
      cargarRecursos();
    });
  </script>
</body>
</html>
"""
