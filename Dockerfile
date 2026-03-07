FROM python:3.12-slim

# HF Spaces ejecuta como usuario 1000
RUN useradd -m -u 1000 appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Crear carpetas con permisos para el usuario
RUN mkdir -p graficos Informes && chown -R appuser:appuser /app

USER appuser

EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
