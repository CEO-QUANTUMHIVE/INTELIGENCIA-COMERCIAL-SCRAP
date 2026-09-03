"""Catálogo estructurado de Programas de Créditos Cloud, Developers y Beneficios Educativos."""

from aplicacion.modelos_recursos import (
    CategoriaRecurso,
    FiltroRecursos,
    Recurso,
    TipoCorreoRequerido,
)

CATALOGO_RECURSOS: list[Recurso] = [
    # ─── BENEFICIOS EDUCATIVOS (IDENTIDAD UNIVERSITARIA) ───────────────────────
    Recurso(
        id="github-student-pack",
        nombre="GitHub Student Developer Pack",
        proveedor="GitHub & Partners",
        categoria=CategoriaRecurso.EDUCATIVO,
        beneficio_principal="GitHub Copilot Gratis + $200k en herramientas (JetBrains, Azure, Namecheap, Canva, DigitalOcean)",
        monto_estimado_usd=200000.0,
        correo_requerido=TipoCorreoRequerido.ESTUDIANTE,
        requisitos=[
            "Correo institucional verificable o certificado de alumno regular",
            "Cuenta de GitHub activa",
            "Ubicación / foto de credencial o portal universitario",
        ],
        dificultad_aprobacion="Baja",
        tiempo_respuesta="1-3 días (o instantáneo)",
        url_oficial="https://education.github.com/pack",
        descripcion="El paquete de beneficios más completo para desarrolladores estudiantes. Incluye acceso gratuito a GitHub Copilot, dominios gratis (.me), hosting, bases de datos y licencias IDEs.",
        instrucciones_postulacion=[
            "1. Entrar a education.github.com/pack con tu cuenta de GitHub",
            "2. Agregar y verificar tu correo universitario en la configuración de GitHub",
            "3. Subir comprobante si lo solicita y aprobar el pack",
        ],
        tags=["estudiante", "github", "copilot", "jetbrains", "cloud", "gratis"],
    ),
    Recurso(
        id="azure-for-students",
        nombre="Microsoft Azure for Students",
        proveedor="Microsoft",
        categoria=CategoriaRecurso.EDUCATIVO,
        beneficio_principal="$100 USD anuales en créditos Azure + más de 55 servicios siempre gratuitos sin tarjeta de crédito",
        monto_estimado_usd=100.0,
        correo_requerido=TipoCorreoRequerido.ESTUDIANTE,
        requisitos=[
            "Correo universitario o autenticación institucional",
            "No requiere tarjeta de crédito para registrarse",
        ],
        dificultad_aprobacion="Baja",
        tiempo_respuesta="Instantáneo",
        url_oficial="https://azure.microsoft.com/es-es/free/students/",
        descripcion="Créditos anuales renovables para desplegar máquinas virtuales, bases de datos SQL/NoSQL, servicios de Cognitive Services y Azure OpenAI sin riesgo de cobro accidental.",
        instrucciones_postulacion=[
            "1. Ingresar al enlace oficial y hacer clic en 'Comenzar gratis'",
            "2. Validar con el correo emitido por tu universidad",
            "3. Acceder al portal de Azure con el saldo acreditado automáticamente",
        ],
        tags=["estudiante", "azure", "cloud", "sin_tarjeta", "microsoft"],
    ),
    Recurso(
        id="jetbrains-student",
        nombre="JetBrains Educational License Pack",
        proveedor="JetBrains",
        categoria=CategoriaRecurso.EDUCATIVO,
        beneficio_principal="Acceso 100% gratuito a todas las herramientas profesionales (PyCharm Pro, IntelliJ Ultimate, DataGrip, WebStorm)",
        monto_estimado_usd=650.0,
        correo_requerido=TipoCorreoRequerido.ESTUDIANTE,
        requisitos=[
            "Correo universitario activo",
        ],
        dificultad_aprobacion="Baja",
        tiempo_respuesta="Instantáneo",
        url_oficial="https://www.jetbrains.com/community/education/#students",
        descripcion="Licencia profesional completa de la suite JetBrains para desarrollo en Python, Java, JavaScript, bases de datos y C++, renovable cada año mientras seas estudiante.",
        instrucciones_postulacion=[
            "1. Registrarse en JetBrains con tu email universitario",
            "2. Confirmar el link de verificación recibido en el buzón universitario",
            "3. Descargar y activar cualquier IDE con tu cuenta de JetBrains",
        ],
        tags=["estudiante", "jetbrains", "pycharm", "ide", "desarrollo"],
    ),
    Recurso(
        id="aws-educate",
        nombre="AWS Educate & Student Grants",
        proveedor="Amazon Web Services",
        categoria=CategoriaRecurso.EDUCATIVO,
        beneficio_principal="Créditos para laboratorios en la nube de AWS + acceso a cursos y certificaciones oficiales sin tarjeta de crédito",
        monto_estimado_usd=100.0,
        correo_requerido=TipoCorreoRequerido.ESTUDIANTE,
        requisitos=["Correo institucional o registro estudiantil"],
        dificultad_aprobacion="Baja",
        tiempo_respuesta="1-2 días",
        url_oficial="https://aws.amazon.com/es/education/awseducate/",
        descripcion="Entorno de aprendizaje y créditos en la nube de Amazon Web Services para practicar arquitecturas, serverless, S3 y computación en la nube.",
        instrucciones_postulacion=[
            "1. Registrarse con email institucional en el portal de AWS Educate",
            "2. Completar los datos de tu institución",
            "3. Acceder a la consola de laboratorios con saldo habilitado",
        ],
        tags=["estudiante", "aws", "cloud", "amazon"],
    ),
    Recurso(
        id="notion-for-education",
        nombre="Notion for Education (Plus Plan + AI)",
        proveedor="Notion Labs",
        categoria=CategoriaRecurso.EDUCATIVO,
        beneficio_principal="Plan Plus gratuito de por vida estudiantil (páginas ilimitadas, historial de versiones y subida de archivos pesados)",
        monto_estimado_usd=120.0,
        correo_requerido=TipoCorreoRequerido.ESTUDIANTE,
        requisitos=["Cuenta de Notion asociada a correo universitario admitido"],
        dificultad_aprobacion="Baja",
        tiempo_respuesta="Instantáneo",
        url_oficial="https://www.notion.so/product/notion-for-education",
        descripcion="Workspace ilimitado para gestión de proyectos, documentación de código, bases de datos y apuntes con el plan Plus desbloqueado.",
        instrucciones_postulacion=[
            "1. Cambiar o registrar el email de tu cuenta Notion a tu correo universitario",
            "2. Ir a Configuración -> Facturación -> 'Obtener plan para estudiantes'",
        ],
        tags=["estudiante", "notion", "productividad", "documentacion"],
    ),
    Recurso(
        id="figma-education",
        nombre="Figma & FigJam for Education",
        proveedor="Figma",
        categoria=CategoriaRecurso.EDUCATIVO,
        beneficio_principal="Plan Figma Professional gratis (proyectos ilimitados, librerías compartidas de diseño y modo Dev)",
        monto_estimado_usd=180.0,
        correo_requerido=TipoCorreoRequerido.ESTUDIANTE,
        requisitos=["Correo universitario o acreditación de estudios"],
        dificultad_aprobacion="Baja",
        tiempo_respuesta="Instantáneo",
        url_oficial="https://www.figma.com/education/",
        descripcion="Herramienta de diseño UI/UX líder con todas las funcionalidades de equipo y Dev Mode desbloqueadas para crear interfaces y prototipos.",
        instrucciones_postulacion=[
            "1. Aplicar en figma.com/education con tu cuenta",
            "2. Seleccionar tu universidad y subir prueba si es requerida",
            "3. Crear equipos educativos gratuitos",
        ],
        tags=["estudiante", "figma", "diseño", "ui_ux"],
    ),

    # ─── CRÉDITOS CLOUD & STARTUPS (CORREO CORPORATIVO / DOMINIO PROPIO) ─────
    Recurso(
        id="microsoft-founders-hub",
        nombre="Microsoft for Startups Founders Hub",
        proveedor="Microsoft",
        categoria=CategoriaRecurso.CLOUD,
        beneficio_principal="Hasta $150,000 en créditos Azure + $2,500 en créditos OpenAI (GPT-4o, o1) + GitHub Enterprise + LinkedIn Premium",
        monto_estimado_usd=150000.0,
        correo_requerido=TipoCorreoRequerido.CORPORATIVO,
        requisitos=[
            "Correo corporativo (@tudominio.com)",
            "Perfil de LinkedIn activo y profesional",
            "Página web del proyecto o prototipo funcional",
            "No requiere haber levantado capital previo (abierto a etapa idea / bootstrap)",
        ],
        dificultad_aprobacion="Media",
        tiempo_respuesta="2-5 días hábiles",
        url_oficial="https://foundershub.startups.microsoft.com/",
        descripcion="El programa más generoso para startups de tecnología e Inteligencia Artificial. Comienza otorgando $1k a $5k en Azure y escala hasta $150k a medida que se usa la plataforma, incluyendo créditos directos en la API de OpenAI.",
        instrucciones_postulacion=[
            "1. Ingresar con una cuenta vinculada a tu LinkedIn o correo de dominio propio",
            "2. Completar nombre de la startup, web y descripción del producto",
            "3. Detallar cómo usarás Azure y OpenAI en tu arquitectura",
        ],
        tags=["cloud", "azure", "openai", "startups", "corporativo", "ia"],
    ),
    Recurso(
        id="aws-activate-founders",
        nombre="AWS Activate Founders",
        proveedor="Amazon Web Services",
        categoria=CategoriaRecurso.CLOUD,
        beneficio_principal="$1,000 a $100,000 USD en créditos AWS + 1 año de soporte técnico para desarrolladores + plantillas de infraestructura",
        monto_estimado_usd=5000.0,
        correo_requerido=TipoCorreoRequerido.CORPORATIVO,
        requisitos=[
            "Correo con dominio corporativo propio",
            "Sitio web de la empresa activo y público",
            "Cuenta de AWS activa con tarjeta registrada",
            "Perfil de LinkedIn de la empresa o fundador",
        ],
        dificultad_aprobacion="Media",
        tiempo_respuesta="3-7 días",
        url_oficial="https://aws.amazon.com/es/activate/founders/",
        descripcion="Créditos para infraestructura en AWS (EC2, S3, RDS, Bedrock, SageMaker). El paquete Founders está pensado para proyectos autofinanciados (bootstrapped) sin necesidad de aceleradora.",
        instrucciones_postulacion=[
            "1. Iniciar sesión en la consola de AWS con tu cuenta",
            "2. Ir a la sección AWS Activate y seleccionar paquete Founders / Self-Funded",
            "3. Enviar URL de la empresa y descripción de la solución",
        ],
        tags=["cloud", "aws", "startups", "corporativo", "infraestructura"],
    ),
    Recurso(
        id="google-cloud-startups",
        nombre="Google for Startups Cloud Program",
        proveedor="Google Cloud",
        categoria=CategoriaRecurso.CLOUD,
        beneficio_principal="Hasta $2,000 a $350,000 USD en créditos GCP y Firebase + soporte de arquitectura de Google Cloud",
        monto_estimado_usd=2000.0,
        correo_requerido=TipoCorreoRequerido.CORPORATIVO,
        requisitos=[
            "Cuenta corporativa (Google Workspace o dominio corporativo propio)",
            "Web pública del proyecto",
            "Facturación de Google Cloud configurada",
        ],
        dificultad_aprobacion="Media",
        tiempo_respuesta="3-5 días",
        url_oficial="https://cloud.google.com/startup",
        descripcion="Créditos para servicios de Google Cloud (Compute Engine, BigQuery, Vertex AI, Gemini API en Google Cloud y Firebase).",
        instrucciones_postulacion=[
            "1. Crear o tener un proyecto en Google Cloud Console",
            "2. Postular en el sitio de Startups con el dominio de la empresa",
            "3. Especificar qué servicios de GCP/Vertex AI se utilizarán",
        ],
        tags=["cloud", "google_cloud", "firebase", "vertex_ai", "gemini", "startups"],
    ),
    Recurso(
        id="oracle-cloud-startups",
        nombre="Oracle for Startups / Free Tier",
        proveedor="Oracle Cloud",
        categoria=CategoriaRecurso.CLOUD,
        beneficio_principal="$300 en créditos iniciales + 4 OCPU ARM Ampere y 24GB RAM 100% SIEMPRE GRATIS (Always Free)",
        monto_estimado_usd=500.0,
        correo_requerido=TipoCorreoRequerido.CUALQUIERA,
        requisitos=[
            "Tarjeta de crédito para verificación de identidad ($0 cobrado)",
            "Correo válido",
        ],
        dificultad_aprobacion="Baja",
        tiempo_respuesta="Instantáneo",
        url_oficial="https://www.oracle.com/cloud/free/",
        descripcion="El nivel gratuito más potente del mercado: permite tener hasta 4 servidores virtuales ARM con 24 GB de memoria RAM y 200 GB de almacenamiento SSD sin pagar nunca.",
        instrucciones_postulacion=[
            "1. Registrarse en Oracle Cloud Free Tier",
            "2. Validar identidad con tarjeta de crédito",
            "3. Crear instancias de cómputo Always Free",
        ],
        tags=["cloud", "oracle", "always_free", "vps", "gratis"],
    ),
    Recurso(
        id="digitalocean-hatch",
        nombre="DigitalOcean Hatch Startup Program",
        proveedor="DigitalOcean",
        categoria=CategoriaRecurso.CLOUD,
        beneficio_principal="$1,000 a $10,000 USD en créditos de infraestructura durante 12 meses + soporte prioritario",
        monto_estimado_usd=1000.0,
        correo_requerido=TipoCorreoRequerido.CORPORATIVO,
        requisitos=[
            "Correo corporativo",
            "Sitio web del proyecto",
            "No haber recibido créditos Hatch previos",
        ],
        dificultad_aprobacion="Baja",
        tiempo_respuesta="2-4 días",
        url_oficial="https://www.digitalocean.com/hatch",
        descripcion="Créditos para Droplets, Kubernetes, Bases de Datos Gestionadas y App Platform de DigitalOcean.",
        instrucciones_postulacion=[
            "1. Crear cuenta en DigitalOcean con correo corporativo",
            "2. Completar el formulario de postulación a Hatch",
            "3. Recibir el código de crédito tras revisión",
        ],
        tags=["cloud", "digitalocean", "droplets", "startups"],
    ),

    # ─── PROGRAMAS DE IA & DEVELOPERS ─────────────────────────────────────────
    Recurso(
        id="nvidia-inception",
        nombre="NVIDIA Inception Program",
        proveedor="NVIDIA",
        categoria=CategoriaRecurso.AI_STARTUP,
        beneficio_principal="Descuentos preferenciales en GPUs/hardware NVIDIA + créditos cloud con partners + acceso a cursos DLI y software SDKs de IA",
        monto_estimado_usd=10000.0,
        correo_requerido=TipoCorreoRequerido.CORPORATIVO,
        requisitos=[
            "Correo corporativo propio",
            "Sitio web activo donde se detalle el producto o solución de IA",
            "Estar desarrollando un producto basado en software, datos o IA",
        ],
        dificultad_aprobacion="Media",
        tiempo_respuesta="1-2 semanas",
        url_oficial="https://www.nvidia.com/es-la/startups/",
        descripcion="Programa global para startups de Inteligencia Artificial. Brinda acceso a ingenieros de NVIDIA, créditos en la nube (AWS, Azure, GCP, Lambda Labs) y descuentos en hardware NVIDIA RTX/H100.",
        instrucciones_postulacion=[
            "1. Llenar el formulario oficial en nvidia.com/startups",
            "2. Indicar modelos de IA utilizados (LLMs, Computer Vision, Embeddings, etc.)",
            "3. Enviar enlace de demo, repositorio o web",
        ],
        tags=["ia", "nvidia", "gpus", "deep_learning", "startups", "corporativo"],
    ),
    Recurso(
        id="github-for-startups",
        nombre="GitHub for Startups",
        proveedor="GitHub",
        categoria=CategoriaRecurso.DEV_TOOLS,
        beneficio_principal="Hasta 20 licencias de GitHub Enterprise gratis por 1 año + acceso preferencial a productos beta",
        monto_estimado_usd=5000.0,
        correo_requerido=TipoCorreoRequerido.CORPORATIVO,
        requisitos=[
            "Correo con dominio corporativo",
            "Organización de GitHub creada",
            "Estar en etapa Seed o Bootstrap (hasta Serie A)",
        ],
        dificultad_aprobacion="Media",
        tiempo_respuesta="3-5 días",
        url_oficial="https://github.com/enterprise/startups",
        descripcion="Paquete empresarial de GitHub para gestionar equipos, CI/CD con GitHub Actions avanzadas, escaneo de seguridad y control de código.",
        instrucciones_postulacion=[
            "1. Crear una organización en GitHub con tu dominio",
            "2. Postular a través del portal de GitHub for Startups",
        ],
        tags=["dev_tools", "github", "enterprise", "startups", "corporativo"],
    ),
    Recurso(
        id="cloudflare-for-startups",
        nombre="Cloudflare for Startups",
        proveedor="Cloudflare",
        categoria=CategoriaRecurso.DEV_TOOLS,
        beneficio_principal="Hasta $250,000 en créditos de Cloudflare (Workers, KV, Vectorize, R2 Storage, AI Gateway y Enterprise Security)",
        monto_estimado_usd=250000.0,
        correo_requerido=TipoCorreoRequerido.CORPORATIVO,
        requisitos=[
            "Correo corporativo",
            "Dominio configurado en Cloudflare",
            "Producto de base tecnológica",
        ],
        dificultad_aprobacion="Media",
        tiempo_respuesta="5-10 días",
        url_oficial="https://www.cloudflare.com/lp/startups/",
        descripcion="Infraestructura edge serverless y seguridad para desplegar APIs globales, proxies, bases de datos vectoriales y almacenamiento S3 sin costos de egreso.",
        instrucciones_postulacion=[
            "1. Añadir tu dominio a una cuenta de Cloudflare",
            "2. Postular en el portal de startups indicando tu arquitectura serverless",
        ],
        tags=["dev_tools", "cloudflare", "edge", "workers", "ia_gateway", "seguridad"],
    ),
    Recurso(
        id="mongodb-for-startups",
        nombre="MongoDB for Startups",
        proveedor="MongoDB",
        categoria=CategoriaRecurso.DEV_TOOLS,
        beneficio_principal="$500 a $5,000 en créditos MongoDB Atlas + 1 hora de consultoría con arquitectos de datos",
        monto_estimado_usd=2000.0,
        correo_requerido=TipoCorreoRequerido.CORPORATIVO,
        requisitos=[
            "Correo corporativo",
            "Cuenta de MongoDB Atlas activa",
            "Web de la startup",
        ],
        dificultad_aprobacion="Baja",
        tiempo_respuesta="3-5 días",
        url_oficial="https://www.mongodb.com/startups",
        descripcion="Créditos para bases de datos NoSQL documentales y búsqueda vectorial integrada (Atlas Vector Search) para agentes de IA.",
        instrucciones_postulacion=[
            "1. Registrarse en MongoDB Atlas con correo de la empresa",
            "2. Completar la solicitud en mongodb.com/startups",
        ],
        tags=["dev_tools", "mongodb", "base_datos", "vector_search", "startups"],
    ),

    # ─── SAAS PERKS & SUBSIDIOS ──────────────────────────────────────────────
    Recurso(
        id="stripe-atlas-perks",
        nombre="Stripe Startup Perks & Fee Credits",
        proveedor="Stripe",
        categoria=CategoriaRecurso.SAAS_PERKS,
        beneficio_principal="$20,000 en procesamiento de pagos sin comisiones + acceso a descuentos exclusivos de software",
        monto_estimado_usd=1000.0,
        correo_requerido=TipoCorreoRequerido.CORPORATIVO,
        requisitos=[
            "Cuenta de Stripe corporativa",
            "Sitio web donde se ofrecerán servicios o productos",
        ],
        dificultad_aprobacion="Baja",
        tiempo_respuesta="2-3 días",
        url_oficial="https://stripe.com/startups",
        descripcion="Exoneración de comisiones de procesamiento de tarjetas de crédito y acceso a perks de terceros.",
        instrucciones_postulacion=[
            "1. Abrir cuenta en Stripe con dominio corporativo",
            "2. Postular a través del portal de startups de Stripe o incubadora aliada",
        ],
        tags=["saas_perks", "stripe", "pagos", "startups", "corporativo"],
    ),
    Recurso(
        id="hubspot-for-startups",
        nombre="HubSpot for Startups",
        proveedor="HubSpot",
        categoria=CategoriaRecurso.SAAS_PERKS,
        beneficio_principal="30% a 90% de descuento en la suite profesional de HubSpot (CRM, Email Marketing, Automatizaciones)",
        monto_estimado_usd=3000.0,
        correo_requerido=TipoCorreoRequerido.CORPORATIVO,
        requisitos=[
            "Correo corporativo",
            "Startup en etapa temprana",
        ],
        dificultad_aprobacion="Baja",
        tiempo_respuesta="2-3 días",
        url_oficial="https://www.hubspot.com/startups",
        descripcion="Plataforma líder para gestión de leads, seguimiento de ventas y automatización de marketing con descuento masivo para emprendedores.",
        instrucciones_postulacion=[
            "1. Llenar el formulario en hubspot.com/startups con tu correo corporativo",
            "2. Seleccionar el plan deseado con el código de descuento aplicado",
        ],
        tags=["saas_perks", "hubspot", "crm", "marketing", "startups"],
    ),
]


def filtrar_recursos(filtro: FiltroRecursos) -> list[Recurso]:
    """Filtra los recursos del catálogo según los criterios del usuario."""
    resultado = list(CATALOGO_RECURSOS)

    # Filtro por categoría
    if filtro.categoria:
        resultado = [r for r in resultado if r.categoria == filtro.categoria]

    # Filtro por tipo de correo disponible
    # Si el usuario especificó qué correos tiene:
    if filtro.tiene_correo_estudiante or filtro.tiene_correo_corporativo:
        permitidos = [TipoCorreoRequerido.CUALQUIERA]
        if filtro.tiene_correo_estudiante:
            permitidos.append(TipoCorreoRequerido.ESTUDIANTE)
        if filtro.tiene_correo_corporativo:
            permitidos.append(TipoCorreoRequerido.CORPORATIVO)
        resultado = [r for r in resultado if r.correo_requerido in permitidos]

    # Búsqueda por texto (nombre, proveedor, beneficio, tags)
    if filtro.texto_busqueda:
        termino = filtro.texto_busqueda.strip().lower()
        resultado = [
            r for r in resultado
            if termino in r.nombre.lower()
            or termino in r.proveedor.lower()
            or termino in r.beneficio_principal.lower()
            or termino in r.descripcion.lower()
            or any(termino in tag.lower() for tag in r.tags)
        ]

    return resultado


def obtener_recurso(recurso_id: str) -> Recurso | None:
    """Devuelve un recurso por su ID único."""
    for r in CATALOGO_RECURSOS:
        if r.id == recurso_id:
            return r
    return None
