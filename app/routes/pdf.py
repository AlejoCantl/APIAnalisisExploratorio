# app/routes/pdf.py
# Endpoint para generar el informe PDF con los resultados del EDA.

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import PdfRequest, PdfResponse
from app.services.pdf_service import PdfService
from app.routes.analisis import _analisis_service_cache

router = APIRouter()


@router.post("/generar", response_model=PdfResponse)
async def generar_pdf(
    request: PdfRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Genera el informe PDF usando los resultados del último EDA ejecutado.
    Requiere que /analisis/ejecutar haya corrido antes.
    """
    # Verificar que haya resultados del análisis
    service_cache = _analisis_service_cache.get("ultima")
    if service_cache is None:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail="No hay resultados de análisis. Ejecute primero /analisis/ejecutar"
        )

    # Incluir outliers solo si el usuario lo pide Y se ejecutó tratar-outliers antes
    outliers_data = None
    if request.incluir_outliers:
        outliers_data = _analisis_service_cache.get("outliers")
        if outliers_data is None:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400,
                detail="No hay resultados de outliers. Ejecute primero /analisis/tratar-outliers"
            )

    pdf_service = PdfService(db)
    return await pdf_service.generar_pdf(
        dataset_id=request.dataset_id,
        resultados=service_cache.resultados,
        rutas_graficos=service_cache.rutas_graficos,
        outliers_data=outliers_data,
    )