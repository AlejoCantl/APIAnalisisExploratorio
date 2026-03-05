# app/database.py

import os
import re
import ssl
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

load_dotenv()

# Lee la URL del .env y reemplaza 'postgresql://' por 'postgresql+asyncpg://'
# asyncpg es compatible con Windows (ProactorEventLoop)
_raw_url = os.getenv('DATABASE_URL', '')
DATABASE_URL = re.sub(r'^postgresql://', 'postgresql+asyncpg://', _raw_url)

# asyncpg no soporta sslmode ni channel_binding como parámetros de URL
DATABASE_URL = re.sub(r'[&?](sslmode|channel_binding)=[^&]*', '', DATABASE_URL)

# SSL context para Neon (equivalente a sslmode=require)
_ssl_ctx = ssl.create_default_context()

# Crea el motor asíncrono
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,    # maneja el cold start de Neon
    pool_recycle=300,       # renueva conexiones cada 5 minutos
    connect_args={"ssl": _ssl_ctx}
)

# Fábrica de sesiones asíncronas
# expire_on_commit=False evita que los objetos expiren al hacer commit
SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# Clase base de la que heredan todos los modelos ORM
Base = declarative_base()


# Generador de sesiones — inyectado en los routes vía Depends(get_db)
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session        # entrega la sesión al endpoint
        finally:
            await session.close() # siempre se cierra al terminar