# app/routes/datos.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    CargarDatosRequest, CargarDatosResponse,
    ColumnasResponse, EstadoResponse
)
from app.services.datos_service import DatosService

router = APIRouter()

# Instancia global — persiste el DataFrame entre peticiones
_service: DatosService | None = None


async def get_datos_service(db: AsyncSession = Depends(get_db)) -> DatosService:
    """Retorna la instancia global de DatosService con sesión fresca."""
    global _service
    if _service is None:
        _service = DatosService(db)
    else:
        _service.db = db  # actualiza la sesión sin perder el DataFrame
    return _service


@router.post("/cargar", response_model=CargarDatosResponse)
async def cargar_datos(request: CargarDatosRequest,
                       service: DatosService = Depends(get_datos_service)):
    return await service.cargar_datos(request.url, request.tipo, request.sesion_id)


@router.get("/columnas", response_model=ColumnasResponse)
async def obtener_columnas(service: DatosService = Depends(get_datos_service)):
    return await service.obtener_columnas()


@router.get("/estado", response_model=EstadoResponse)
async def obtener_estado(service: DatosService = Depends(get_datos_service)):
    return service.obtener_estado()