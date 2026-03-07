# app/routes/sesiones.py

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Sesion, Usuario
from app.schemas import SesionCreate, SesionResponse, CancelarSesionRequest, CancelarSesionResponse

router = APIRouter()


@router.post("/crear", response_model=SesionResponse)
async def crear_sesion(request: SesionCreate, db: AsyncSession = Depends(get_db)):
    # Buscar si ya existe un usuario con exactamente el mismo nombre y apellido
    result = await db.execute(
        select(Usuario).where(
            Usuario.nombre == request.nombre,
            Usuario.apellido == request.apellido,
        )
    )
    usuario = result.scalar_one_or_none()
    usuario_nuevo = False

    if usuario is None:
        # Crear usuario nuevo
        usuario = Usuario(nombre=request.nombre, apellido=request.apellido)
        db.add(usuario)
        await db.flush()  # genera el ID sin hacer commit todavía
        usuario_nuevo = True

    # Crear la sesión enlazada al usuario
    sesion = Sesion(usuario_id=usuario.id)
    db.add(sesion)
    await db.commit()
    await db.refresh(sesion)
    await db.refresh(usuario)

    nombre_completo = f"{usuario.nombre} {usuario.apellido}"
    mensaje = (
        f"Sesión iniciada correctamente para {nombre_completo}"
        if usuario_nuevo
        else f"Bienvenido de nuevo, {nombre_completo}"
    )

    return SesionResponse(
        sesion_id=sesion.id,
        usuario_id=usuario.id,
        mensaje=mensaje,
        usuario_nuevo=usuario_nuevo,
    )


@router.post("/cancelar", response_model=CancelarSesionResponse)
async def cancelar_sesion(request: CancelarSesionRequest, db: AsyncSession = Depends(get_db)):
    """Marca una sesión como cancelada — el usuario decidió no continuar."""
    result = await db.execute(
        select(Sesion).where(Sesion.id == request.sesion_id)
    )
    sesion = result.scalar_one_or_none()

    if sesion is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    if sesion.estado_sesion != "activa":
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail=f"La sesión ya está '{sesion.estado_sesion}', no se puede cancelar"
        )

    sesion.estado_sesion = "cancelada"
    await db.commit()

    return CancelarSesionResponse(
        mensaje="Sesión cancelada correctamente",
        estado="cancelada",
    )
