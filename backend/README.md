# Gestor de Personal y Operaciones de Campo (Backend)

Backend en **Python + FastAPI** para gestionar:

- Empleados y autenticación.
- Fichajes de entrada/salida (control horario).
- (En progreso) Gestión de ausencias, órdenes de trabajo, etc.

Este servicio expone una API REST documentada con Swagger/OpenAPI y usa **PostgreSQL** como base de datos a través de **SQLAlchemy**.

---

## 🧱 Stack técnico

- **Lenguaje:** Python 3.13
- **Framework web:** FastAPI
- **Servidor ASGI:** Uvicorn
- **ORM:** SQLAlchemy
- **Validación de datos:** Pydantic v2
- **Autenticación:** OAuth2 (password flow) + JWT (`python-jose`)
- **Hash de contraseñas:** `passlib` (algoritmo `pbkdf2_sha256`)
- **Base de datos:** PostgreSQL (local)
- **Driver PostgreSQL:** `psycopg2-binary`
- **Otros:** `python-multipart` (formularios), etc.

---

## 📁 Estructura del proyecto (backend)

Desde la carpeta `backend/`:

```text
backend/
  app/
    __init__.py
    main.py              # Punto de entrada de FastAPI
    config.py            # Configuración de la app (BD, JWT, etc.)
    database.py          # Conexión a la BD y sesión SQLAlchemy

    models/              # Modelos de BD (tablas)
      __init__.py
      employee.py        # Tabla employees
      time_entry.py      # Tabla time_entries
      # (más adelante: absence.py, work_order.py, etc.)

    schemas/             # Esquemas Pydantic (entrada/salida API)
      __init__.py
      employee.py        # EmployeeBase, EmployeeCreate, EmployeeRead
      auth.py            # Token, TokenData, LoginRequest
      time_entry.py      # TimeEntryRead

    utils/
      __init__.py
      security.py        # Hash de password + generación/decodificación de JWT

    routers/
      __init__.py
      auth_router.py         # /api/auth/login
      employees_router.py    # /api/employees/...
      time_entries_router.py # /api/time-entries/...

  create_admin.py        # Script CLI para crear el primer usuario admin
  reset_password.py      # Script CLI para resetear passwords
  requirements.txt       # Dependencias del backend
  .gitignore             # Ignora .venv, app.db, __pycache__, etc.


# Crear el entorno virtual
python -m venv .venv

# Activar en Windows (PowerShell)
.\.venv\Scripts\activate

# En macOS/Linux sería algo como:
# source .venv/bin/activate
