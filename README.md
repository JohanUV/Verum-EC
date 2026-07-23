# Verum

> **Proyecto final de Usabilidad** — versión rediseñada de la plataforma para las personas de prueba y la evaluación docente. El sistema original (`verifik-ec/`) se conserva intacto; aquí se aplican las mejoras de usabilidad sugeridas.

Plataforma web para **verificar antecedentes de una persona** en Ecuador a partir de su número de cédula. Consulta en paralelo varias fuentes públicas y genera un informe consolidado con semáforo de riesgo, resultados **agrupados por categoría** y validación de datos de entrada.

**Nombre y marca:** se eligió *Verum* (latín, «la verdad») tras verificar que *Verifik* ya corresponde a una empresa activa del mismo sector (verifik.co), para evitar conflicto de marca.

## Fuentes integradas

| Fuente | Tipo | Estado |
|--------|------|--------|
| Procesos Judiciales (Función Judicial) | API en vivo | ✅ Real |
| SRI – Contribuyente / RUC / Deudas / Establecimientos | API en vivo | ✅ Real |
| Pensiones Alimenticias (SUPA) | API en vivo | ✅ Real |
| Multas de Tránsito (ANT) | API en vivo | ✅ Real |
| Listas de Sanción (OFAC / ONU) | API en vivo | ✅ Real (cotejo por nombre) |
| Título de Bachiller (MinEduc) | Consulta con captcha | 🔓 Relay de captcha |
| Títulos Educación Superior (SENESCYT) | Consulta con captcha | 🔓 Relay de captcha |
| Registro Social (MIES) | Manual asistido | ⚠️ reCAPTCHA + LOPDP (botón a SIIRS) |
| Récord Policial (antecedentes penales) | Informativo | ⚠️ Enlace oficial (captcha) |

> **Relay de captcha:** las fuentes JSF protegidas con captcha de imagen (Bachiller, SENESCYT) se consultan dentro de la app: Verum abre la sesión, muestra la imagen del captcha y el usuario la resuelve; no se intenta romper el captcha automáticamente.
>
> **Registro Social** usa reCAPTCHA v2 de Google (no relayable) y exige la fecha de expedición de la cédula, por lo que la consulta es manual asistida: el botón copia la cédula y abre el portal oficial del SIIRS.

Funciones adicionales: búsqueda por cédula **o** por nombres, semáforo y score de riesgo, historial/auditoría (LOPDP), roles y permisos, y exportación a PDF con folio y marca de agua.

## Cómo ejecutar

```bash
cd proyectoFinalUsabilidad/backend
pip install -r requirements.txt
python run.py
```

Abrir: http://127.0.0.1:5001

**Usuarios de prueba:** `admin` / `admin123` &nbsp;|&nbsp; `analista` / `verum2026`

> No se necesita Node para ejecutar la app: el bundle React ya compilado se
> incluye en `backend/app/static/dist/`. Node solo hace falta para modificar el frontend.

## Frontend (React + Vite)

La interfaz principal es una SPA React que consume la API JSON de Flask.
Para modificarla:

```bash
cd frontend
npm install
npm run build      # compila a backend/app/static/dist/ (o npm run watch mientras editas)
npm run test       # pruebas de componentes y utilidades (vitest)
```

## Pruebas del backend

```bash
cd backend
python -m pytest tests/
```

## Estructura

El repositorio se divide en dos proyectos: **backend** (Flask) y **frontend** (React).

```
proyectoFinalUsabilidad/
├── backend/                       # ---------- Proyecto Flask ----------
│   ├── run.py                     # Punto de entrada (python run.py)
│   ├── requirements.txt
│   ├── data/                      # Generado en ejecución: folio.json, historial.json
│   ├── tests/                     # Pruebas pytest (sin red)
│   └── app/
│       ├── __init__.py            # create_app() — fábrica Flask
│       ├── config.py              # Catálogos y constantes compartidas
│       ├── auth.py                # login_required / permiso_required
│       ├── utils.py               # Validación de cédula, score de riesgo, folio
│       ├── historial.py           # Auditoría de consultas (LOPDP)
│       ├── services.py            # Orquestación: barrido paralelo + informe
│       ├── models/
│       │   └── users.py           #   Usuarios, roles y credenciales
│       ├── forms/
│       │   └── users.py           #   Validación de datos de entrada (login)
│       ├── fuentes/               # Un módulo por fuente consultada
│       │   ├── judicial.py        #   Función Judicial (procesos + litigantes)
│       │   ├── sri.py             #   SRI (RUC, deudas, establecimientos, nombre→cédula)
│       │   ├── supa.py            #   Pensiones alimenticias
│       │   ├── ant.py             #   Multas de tránsito
│       │   ├── sanciones.py       #   OFAC / ONU
│       │   ├── captcha_relay.py   #   Relay de captcha JSF (Bachiller / SENESCYT)
│       │   └── otros.py           #   Récord policial, Registro Social, stubs de títulos
│       ├── routes/
│       │   ├── public.py          #   Rutas públicas (/login)
│       │   ├── users.py           #   Sesión (/api/login, /api/logout)
│       │   ├── private.py         #   Interfaz protegida (/)
│       │   └── api.py             #   API JSON protegida (/api/...)
│       ├── templates/
│       │   ├── users/login.html   #   Pantalla de acceso
│       │   └── private/index.html #   Shell de la SPA React (inyecta permisos)
│       └── static/
│           ├── css/  (styles.css, login.css)
│           ├── js/   (login.js)
│           └── dist/ (app.js — bundle React compilado por Vite)
│
└── frontend/                      # ---------- Proyecto React ----------
    ├── package.json / vite.config.js
    └── src/
        ├── index.jsx              # Punto de montaje
        ├── App.jsx                # Composición: header, pestañas, tema
        ├── routes/                # Definición de secciones y permisos (+ test)
        ├── contexts/
        │   └── ToastContext/      # Notificaciones flotantes
        ├── hooks/
        │   └── useToast/          # Acceso al contexto de notificaciones
        ├── components/            # Componentes compartidos (uno por carpeta, con test)
        │   ├── Loading/  ├── EmptyState/  └── RiskPill/
        ├── pages/                 # Una carpeta por página
        │   ├── PorCedula/         #   + components/: Informe, ResultCard,
        │   │                      #     CaptchaBox, SiirsBox
        │   ├── PorNombre/         #   + components/: ProcesoRow
        │   └── Historial/
        ├── services/              # api/ (cliente HTTP) y pdf/ (informe PDF), con tests
        └── utils/                 # formato/ y sesion/, con tests
```
