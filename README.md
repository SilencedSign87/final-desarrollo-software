# Sistema Académico Integral

## Equipo

- Alaracon Mendoza Estiven Rodrigo
- Araujo Champi José Eduardo
- Diaz Vega Bruno Nivardo


## Tecnologías

**Frontend**
- React 19 + Vite
- React Router DOM (enrutamiento)
- Axios (cliente HTTP)
- Tailwind CSS
- Lucide React (iconos)

**Backend**
- Python + Flask
- flask-openapi3 (framework de rutas + documentación OpenAPI/Swagger)
- SQLAlchemy (ORM) + Flask-Migrate (migraciones)
- Flask-CORS
- Flask sessions (autenticación basada en cookies de servidor, no JWT)
- ReportLab + qrcode (generación de documentos y firma con QR)

**Base de datos**
- SQLite por defecto (`sqlite:///app.db`), configurable a cualquier motor soportado por SQLAlchemy mediante `DATABASE_URL`

## Requisitos previos

Antes de ejecutar el proyecto en otra computadora necesitas:

- **Python 3.10 o superior**
- **Node.js 18 o superior**
- **Git**

Puedes verificar las versiones con:

```bash
python --version
node --version
npm --version
```

## Clonar el proyecto

```bash
git clone <URL-del-repositorio>
cd final-desarrollo-software
```

## Configurar el backend

El backend está en la carpeta `backend`.

1. Entra al backend:

```bash
cd backend
```

2. Crea y activa un entorno virtual:

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

4. Crea un archivo `.env` dentro de `backend` (opcional; si no lo creas, se usan los valores por defecto):

```env
SECRET_KEY=una-clave-secreta-cualquiera
DATABASE_URL=sqlite:///app.db
FRONTEND_URL=http://localhost:3000
PUBLIC_BASE_URL=http://127.0.0.1:5000
```

5. Para crear la base de datos y cargar usuarios/datos de prueba, ejecuta dentro del entorno virtual:

```bash
flask db upgrade
flask seed
```

Este comando (definido en `app/__init__.py`) crea los usuarios por defecto (uno por rol) y los datos de prueba de `app/seed.py`, siempre que la base de datos aún esté vacía.

6. Para iniciar el servidor backend:

```bash
python run.py
```

El backend queda disponible en `http://127.0.0.1:5000`. La documentación interactiva de la API (Swagger/Scalar, generada por flask-openapi3) queda en `http://127.0.0.1:5000/docs`.

## Configurar el frontend

En otra terminal, dejando el backend corriendo:

```bash
cd frontend
npm install
npm run dev
```

El frontend queda disponible en `http://localhost:3000` (Vite hace proxy de `/api` hacia `http://127.0.0.1:5000`, definido en `vite.config.js`).

## Orden recomendado de ejecución

1. Configurar `.env` en `backend` (opcional).
2. Instalar dependencias del backend con `pip install -r requirements.txt`.
3. Ejecutar `flask db upgrade` y `flask seed` para crear la base de datos y los datos semilla.
4. Ejecutar `python run.py` para levantar Flask.
5. Instalar dependencias del frontend con `npm install`.
6. Ejecutar `npm run dev` en `frontend`.

---

## Credenciales de prueba

Al ejecutar `flask db upgrade` y `flask seed`, `app/seed.py` crea automáticamente los siguientes usuarios base, uno por cada rol del sistema:

| Rol | Email | Contraseña |
|---|---|---|
| Administrador | `admin.general@sistema.edu` | `admin123` |
| Dirección | `administrativo@sistema.edu` | `administrativo123` |
| Docente | `docente.50001@sistemas.edu` | `docente123` |
| Estudiante | `estudiante.70001@sistemas.edu` | `estudiante123` |

Además, `seed_test_data()` crea varios docentes y estudiantes adicionales de prueba (contraseña `123456` para la mayoría) con secciones, matrículas y evaluaciones ya cargadas, útiles para probar el sistema con datos reales.

## Arquitectura del sistema

El sistema sigue una arquitectura general de **cliente-servidor desacoplado** (SPA + API REST).

- La comunicación entre frontend y backend se hace exclusivamente vía **HTTP + JSON**.
- La sesión del usuario se maneja con **Flask session** (cookie `httponly` firmada por el servidor), no con JWT: el backend guarda `user_id` en `session` y lo valida en cada petición protegida.
- El backend valida cada endpoint protegido según el **rol** del usuario autenticado, mediante decoradores de middleware.
- CORS está configurado en el backend (`flask-cors`) para aceptar peticiones únicamente desde el origen del frontend, con `supports_credentials=True` para permitir el envío de la cookie de sesión.

### Arquitectura interna del backend (por capas)

El backend usa una **arquitectura en capas (layered architecture)** simple de tipo *Route → Service → Model*, sin separación por módulo de dominio: cada capa vive en su propia carpeta a nivel global y agrupa los archivos por entidad de negocio (sección, docente, curso, matrícula, etc.).

```
backend/app/
├── models/          → Modelos ORM (SQLAlchemy): representan las tablas de la base de datos
├── schemas/         → DTOs de entrada/salida (Pydantic): validan y documentan cada endpoint
├── services/        → Lógica de negocio (reglas, validaciones, consultas al ORM)
├── routes/          → Controlador + endpoint en un mismo archivo (Blueprint de flask-openapi3)
├── middleware/
│   └── auth.py      → auth_required / roles_required: control de acceso por sesión y rol
├── utils/           → Utilidades transversales (fechas, URLs)
├── templates/        → Plantillas HTML (verificación de documentos con QR)
└── seed.py          → Usuarios y datos de prueba para poblar la base de datos
```

Recorrido de un endpoint: **ruta (`routes/`) → servicio (`services/`) → modelo/ORM (`models/`) → base de datos**, validando la entrada/salida con los esquemas Pydantic de `schemas/`, y la respuesta regresa por el mismo camino en sentido inverso, como JSON.

### Estructura del frontend

El frontend usa una organización **por rol de usuario** en lugar de por módulo de negocio: cada tipo de usuario tiene su propia carpeta de vistas.

```
frontend/src/
├── views/
│   ├── Administrativo/   → Vistas del rol administrador (secciones, docentes, cursos, usuarios...)
│   ├── Direccion/        → Vistas del rol dirección (carga docente, reportes...)
│   ├── Docente/          → Vistas del rol docente (secciones, notas, cursos)
│   ├── Estudiante/       → Vistas del rol estudiante (matrícula, notas, documentos)
│   ├── Loginview.jsx / RegisterView.jsx / LoadingView.jsx
├── components/           → Componentes reutilizables (matricula/, security/, documents/, etc.)
├── services/             → Un archivo por entidad, con las llamadas a la API vía Axios (api.js centraliza la instancia)
├── context/
│   └── AuthContext.jsx   → Guarda el usuario autenticado y expone login/logout a toda la app
├── hooks/                → Hooks personalizados
└── utils/                → Utilidades varias
```

El enrutamiento se arma con **React Router DOM**, y el acceso a cada vista se protege verificando el rol guardado en `AuthContext`. El menú de navegación se arma dinámicamente según el rol del usuario autenticado.

### Módulos implementados

| Módulo | Descripción | Roles que interactúan |
|---|---|---|
| Autenticación | Login, registro y sesión con Flask session | Todos |
| Matrícula | Solicitud, validación de prerrequisitos/choques de horario, pagos y comprobantes | Estudiante, Administrador, Dirección |
| Cursos y Docentes | Asignación de secciones, horarios y sílabos (PDF) | Docente, Administrador, Dirección |
| Evaluaciones / Notas | Registro y consulta de notas parciales y finales | Docente, Estudiante, Administrador, Dirección |
| Periodos Académicos | Gestión de semestres activos | Administrador, Dirección |
| Documentos | Solicitud, aprobación y verificación de documentos con firma/QR | Estudiante, Administrador, Dirección |
| Seguridad | Gestión de usuarios y control de acceso por rol | Administrador |

### Seguridad y control de acceso por roles

El sistema define 4 roles: **estudiante**, **docente**, **administrador** y **dirección**. Cada endpoint protegido del backend usa los decoradores de `middleware/auth.py`:

1. `auth_required`: verifica que exista una sesión activa (`session["user_id"]`) y carga el usuario en `g.current_user`.
2. `roles_required(*roles)`: además de validar la sesión, comprueba que el rol del usuario esté dentro de la lista de roles permitidos para ese endpoint.

En el frontend, esto se refuerza mostrando y habilitando solo las rutas y opciones de menú correspondientes al rol del usuario autenticado, guardado en `AuthContext`.
