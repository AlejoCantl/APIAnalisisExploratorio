# app/routes/correo.py
# Endpoint para enviar el informe PDF por correo electrónico.

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import CorreoRequest, CorreoResponse
from app.services.correo_service import CorreoService

router = APIRouter()


@router.post("/enviar", response_model=CorreoResponse)
async def enviar_correo(
    request: CorreoRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Envía el informe PDF al correo indicado por el usuario.
    Requiere que /pdf/generar se haya ejecutado antes.
    """
    service = CorreoService(db)
    return await service.enviar_informe(
        informe_id=request.informe_id,
        correo_destino=request.correo,
        sesion_id=request.sesion_id,
    )