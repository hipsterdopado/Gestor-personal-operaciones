from fastapi import FastAPI

from .database import Base, engine
from .models import employee  # importa modelos para que se creen las tablas
from .routers import auth_router, employees_router
from .routers import time_entries_router 

def create_app() -> FastAPI:
    app = FastAPI(title="Gestor de Personal y Operaciones de Campo")

    # Crear tablas en la BD (solo para desarrollo)
    Base.metadata.create_all(bind=engine)

    # Routers
    app.include_router(auth_router.router, prefix="/api")
    app.include_router(employees_router.router, prefix="/api")
    app.include_router(time_entries_router.router, prefix="/api")

    return app


app = create_app()
