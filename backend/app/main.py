from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .models import employee, time_entry, absence  
from .routers import auth_router, employees_router
from .routers import time_entries_router 
from .routers import absences_router 

def create_app() -> FastAPI:
    app = FastAPI(title="Gestor de Personal y Operaciones de Campo")

    # CORS: permitir peticiones desde el frontend (Vite)
    origins = [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Crear tablas en la BD (solo para desarrollo)
    Base.metadata.create_all(bind=engine)

    # Routers
    app.include_router(auth_router.router, prefix="/api")
    app.include_router(employees_router.router, prefix="/api")
    app.include_router(time_entries_router.router, prefix="/api")
    app.include_router(absences_router.router, prefix="/api") 
    
    return app


app = create_app()
