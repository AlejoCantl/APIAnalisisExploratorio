# app/services/base_service.py
# Clase base de la que heredan todos los services del proyecto.
# Provee sesión de DB, logger por clase y manejo centralizado de errores.

import logging
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    """
    Clase base de la que heredan todos los services.
    Ahora usa AsyncSession en lugar de Session síncrona.
    """

    def __init__(self, db: AsyncSession):
        # Sesión asíncrona de Neon — disponible para todos los hijos
        self.db = db

        # Logger con el nombre de la clase hija
        self.logger = logging.getLogger(type(self).__name__)

    def _handle_error(self, e: Exception, mensaje: str = "Error interno del servidor"):
        """Registra el error y lanza HTTPException."""
        self.logger.error(f"{mensaje}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"{mensaje}: {str(e)}")