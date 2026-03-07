# app/main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import datos, analisis, pdf, correo, sesiones


# Reemplaza @app.on_event('startup') que está deprecado en versiones nuevas
# Crea las tablas en Neon al iniciar — si ya existen no hace nada
# NOTA: tras la reestructuración de usuarios/sesiones, ejecutar con
#       DROP_TABLES=1 para recrear el esquema (esto borra datos existentes).
@asynccontextmanager
async def lifespan(app: FastAPI):
    import os
    async with engine.begin() as conn:
        if os.getenv("DROP_TABLES", "").strip() == "1":
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield  # aquí corre la app
    await engine.dispose()  # al apagar libera todas las conexiones


app = FastAPI(
    title="API Análisis Exploratorio",
    description="Parcial I — EDA con FastAPI + Neon",
    version="1.0.0",
    lifespan=lifespan  # registra el startup/shutdown
)

# Permite peticiones desde cualquier origen — necesario para Java
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra los routers con sus prefijos
app.include_router(sesiones.router, prefix="/sesiones", tags=["Sesiones"])
app.include_router(datos.router,    prefix="/datos",    tags=["Datos"])
app.include_router(analisis.router, prefix="/analisis", tags=["Análisis"])
app.include_router(pdf.router,      prefix="/pdf",      tags=["PDF"])
app.include_router(correo.router,   prefix="/correo",   tags=["Correo"])


@app.get("/")
def root():
    return {"mensaje": "API funcionando correctamente"}