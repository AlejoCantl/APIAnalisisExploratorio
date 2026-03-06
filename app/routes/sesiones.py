# app/routes/sesiones.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Sesion
from app.schemas import SesionCreate, SesionResponse

router = APIRouter()


@router.post("/crear", response_model=SesionResponse)
async def crear_sesion(request: SesionCreate, db: AsyncSession = Depends(get_db)):
    sesion = Sesion(nombre_usuario=request.nombre_usuario)
    db.add(sesion)
    await db.commit()
    await db.refresh(sesion)
    return SesionResponse(sesion_id=sesion.id, mensaje="Sesión iniciada correctamente")
