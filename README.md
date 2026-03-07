# API Análisis Exploratorio

API REST construida con **FastAPI** + **PostgreSQL (Neon)** para ejecutar Análisis Exploratorio de Datos (EDA) sobre datasets públicos.

## Requisitos

- Python 3.12+
- PostgreSQL (Neon)
- Dependencias: `pip install -r requirements.txt`

## Ejecución

```bash
uvicorn app.main:app --reload --port 8000
```

La documentación interactiva (Swagger) estará disponible en: `http://127.0.0.1:8000/docs`

---

## Flujo de uso

Los endpoints deben llamarse **en este orden**:

```
1. POST /sesiones/crear            → obtener sesion_id
2. POST /datos/cargar              → obtener dataset_id
3. GET  /datos/columnas            → ver columnas clasificadas
4. POST /analisis/ejecutar         → ejecutar EDA completo
5. POST /analisis/tratar-outliers  → (opcional) tratar outliers
6. POST /pdf/generar               → generar informe PDF
7. POST /correo/enviar             → enviar PDF por correo
```

> **Nota:** Si el servidor se reinicia, el DataFrame en memoria se pierde y se debe volver a llamar `/datos/cargar` antes de `/analisis/ejecutar`.

> **Nota:** El paso 5 es **opcional**. Solo es necesario si desea incluir la sección de outliers en el informe PDF.

---

## Endpoints

### `GET /` — Health Check

Verifica que la API esté funcionando.

**Request:** Sin body

**Response:**
```json
{
  "mensaje": "API funcionando correctamente"
}
```

---

### `POST /sesiones/crear` — Crear sesión

Registra un nuevo usuario/sesión en la base de datos.

**Request:**
```json
{
  "nombre_usuario": "Alejandro"
}
```

**Response:**
```json
{
  "sesion_id": 5,
  "mensaje": "Sesión iniciada correctamente"
}
```

---

### `POST /datos/cargar` — Cargar dataset

Descarga un dataset desde una URL pública y guarda sus metadatos en Neon.

**Request:**
```json
{
  "url": "https://www.datos.gov.co/resource/ezzu-ke2k.csv",
  "tipo": "csv",
  "sesion_id": 5
}
```

| Campo       | Tipo   | Descripción                                |
|-------------|--------|--------------------------------------------|
| `url`       | string | URL pública del archivo CSV o XLSX         |
| `tipo`      | string | `"csv"` o `"xlsx"`                         |
| `sesion_id` | int    | ID obtenido de `/sesiones/crear`           |

**Response:**
```json
{
  "mensaje": "Conjunto de datos cargados",
  "dataset_id": 6,
  "total_filas": 472,
  "total_columnas": 10,
  "tiene_nulos": true
}
```

---

### `GET /datos/columnas` — Obtener columnas clasificadas

Retorna las columnas del dataset activo, clasificadas automáticamente en cuantitativas y cualitativas.

**Request:** Sin body

**Response:**
```json
{
  "columnas": [
    "item", "no", "a_o", "mes", "barrio_o_vereda",
    "poblacion_beneficiada", "canino_hembra", "canino_macho",
    "felino_hembra", "felino_macho"
  ],
  "cuantitativas": [
    "no", "poblacion_beneficiada", "canino_hembra",
    "canino_macho", "felino_hembra", "felino_macho"
  ],
  "cualitativas": [
    "item", "a_o", "mes", "barrio_o_vereda"
  ]
}
```

---

### `GET /datos/estado` — Estado del proceso

Retorna el estado actual del flujo de trabajo.

**Request:** Sin body

**Response:**
```json
{
  "estado": "cargado"
}
```

| Estado       | Significado                        |
|--------------|------------------------------------|
| `sin_datos`  | No se ha cargado ningún dataset    |
| `analizando` | Descarga/análisis en progreso      |
| `cargado`    | Dataset listo para analizar        |

---

### `POST /analisis/ejecutar` — Ejecutar EDA

Ejecuta el análisis exploratorio completo sobre el dataset cargado. Incluye:

- Detección de valores nulos (antes de limpiar)
- Limpieza de datos (duplicados, nulos, tipos)
- Tablas de frecuencia (cualitativas)
- Estadísticas descriptivas (cuantitativas)
- Tabla de contingencia
- Gráficos PNG (histogramas, boxplots, barras, tortas)

**Request:**
```json
{
  "dataset_id": 6,
  "columnas_cuantitativas": [
    "canino_hembra", "canino_macho",
    "felino_hembra", "felino_macho"
  ],
  "columnas_cualitativas": [
    "no", "barrio_o_vereda", "poblacion_beneficiada"
  ]
}
```

| Campo                      | Tipo     | Descripción                                  |
|----------------------------|----------|----------------------------------------------|
| `dataset_id`               | int      | ID obtenido de `/datos/cargar`               |
| `columnas_cuantitativas`   | string[] | Columnas numéricas a analizar                |
| `columnas_cualitativas`    | string[] | Columnas categóricas a analizar              |

**Response:**
```json
{
  "mensaje": "Análisis completado",
  "graficos": [
    "graficos/cual_no.png",
    "graficos/cual_barrio_o_vereda.png",
    "graficos/cual_poblacion_beneficiada.png",
    "graficos/cuant_canino_hembra.png",
    "graficos/cuant_canino_macho.png",
    "graficos/cuant_felino_hembra.png",
    "graficos/cuant_felino_macho.png"
  ]
}
```

---

### `POST /analisis/tratar-outliers` — Tratar outliers (opcional)

Detecta y reemplaza outliers en columnas cuantitativas usando el método **IQR** (rango intercuartílico). El usuario elige la estrategia de reemplazo: media, mediana o moda. Se generan gráficos comparativos antes/después por cada columna que tenga outliers.

**Request:**
```json
{
  "dataset_id": 6,
  "metodo": "mediana",
  "columnas": ["canino_hembra", "canino_macho", "felino_macho"]
}
```

| Campo        | Tipo     | Descripción                                        |
|--------------|----------|----------------------------------------------------|
| `dataset_id` | int      | ID obtenido de `/datos/cargar`                     |
| `metodo`     | string   | `"media"`, `"mediana"` o `"moda"`                   |
| `columnas`   | string[] | Columnas cuantitativas en las que buscar outliers  |

**Response:**
```json
{
  "mensaje": "Outliers tratados con método 'mediana'",
  "metodo_usado": "mediana",
  "columnas_tratadas": {
    "canino_hembra": {
      "outliers_detectados": 12,
      "valor_reemplazo": 5.0,
      "limite_inferior": -3.5,
      "limite_superior": 15.5,
      "q1": 2.0,
      "q3": 9.0,
      "iqr": 7.0
    },
    "canino_macho": {
      "outliers_detectados": 0,
      "valor_reemplazo": null
    }
  },
  "graficos": [
    "graficos/outliers_canino_hembra.png"
  ]
}
```

> **Nota:** Solo se generan gráficos para columnas que tengan al menos 1 outlier. El DataFrame en memoria queda actualizado con los valores reemplazados.

---

### `POST /pdf/generar` — Generar informe PDF

Genera un informe PDF profesional con todos los resultados del EDA. **Opcionalmente** incluye una sección de tratamiento de outliers si se solicita.

#### Caso 1: PDF estándar (sin outliers)

Genera el informe con las secciones habituales del EDA.

**Request:**
```json
{
  "dataset_id": 6
}
```

> `incluir_outliers` por defecto es `false`, por lo que no es necesario enviarlo.

**Response:**
```json
{
  "mensaje": "Informe generado",
  "informe_id": 1,
  "ruta_pdf": "Informes/informe_6.pdf"
}
```

#### Caso 2: PDF con sección de outliers

Incluye todo lo del caso 1 **más** una sección adicional con:
- Texto interpretativo explicando el tratamiento realizado
- Tabla resumen de outliers por columna
- Gráficos comparativos antes/después

**Requisito previo:** Debe haberse ejecutado `/analisis/tratar-outliers` antes de generar el PDF. Si no se ha ejecutado, el endpoint retorna error 400.

**Request:**
```json
{
  "dataset_id": 6,
  "incluir_outliers": true
}
```

| Campo              | Tipo   | Descripción                                                  |
|--------------------|--------|--------------------------------------------------------------|
| `dataset_id`       | int    | ID obtenido de `/datos/cargar`                               |
| `incluir_outliers` | bool   | `true` para incluir la sección de outliers (default: `false`)|

**Response:**
```json
{
  "mensaje": "Informe generado",
  "informe_id": 2,
  "ruta_pdf": "Informes/informe_6.pdf"
}
```

El PDF incluye:
- Encabezado con franja de color y fecha
- Ficha técnica del dataset
- Nombres de integrantes del equipo
- Interpretación general en lenguaje natural
- Tabla de valores nulos
- Tablas de frecuencia por columna cualitativa
- Estadísticas descriptivas por columna cuantitativa
- Tabla de contingencia
- Gráficos incrustados
- **(Solo si `incluir_outliers: true`)** Sección de tratamiento de outliers con interpretación, tabla y gráficos
- Pie de página con número de página

---

### `POST /correo/enviar` — Enviar informe por correo

Envía el PDF generado al correo indicado.

**Request:**
```json
{
  "informe_id": 1,
  "correo": "usuario@mail.com",
  "nombre_usuario": "Pedro Pablo Pérez Pacheco"
}
```

**Response:**
```json
{
  "mensaje": "Informe enviado",
  "correo": "usuario@mail.com"
}
```

> **Requisito:** Definir `SMTP_EMAIL` y `SMTP_PASSWORD` en el archivo `.env`. Para Gmail, usar una [contraseña de aplicación](https://myaccount.google.com/apppasswords).

---

## Estructura del proyecto

```
app/
├── main.py              # Punto de entrada — FastAPI app + lifespan
├── database.py          # Motor async SQLAlchemy + sesión (Neon)
├── models.py            # Modelos ORM: Sesion, Dataset, Informe
├── schemas.py           # Schemas Pydantic (request/response)
├── routes/
│   ├── sesiones.py      # POST /sesiones/crear
│   ├── datos.py         # POST /datos/cargar, GET /columnas, GET /estado
│   ├── analisis.py      # POST /analisis/ejecutar, POST /analisis/tratar-outliers
│   ├── pdf.py           # POST /pdf/generar (con o sin outliers)
│   └── correo.py        # POST /correo/enviar
└── services/
    ├── base_service.py      # Clase base con logger y manejo de errores
    ├── datos_service.py     # Descarga, limpieza y persistencia de datasets
    ├── analisis_service.py  # EDA: estadísticas, frecuencias, gráficos, interpretación
    ├── pdf_service.py       # Generación de informe PDF con reportlab
    └── correo_service.py    # Envío de PDF por correo (SMTP + HTML)
graficos/                # PNGs generados por el análisis
Informes/                # PDFs generados
```

## Variables de entorno (`.env`)

```env
DATABASE_URL=postgresql://user:pass@host/db
SMTP_EMAIL=correo@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
SMTP_HOST=smtp.gmail.com        # opcional, default: smtp.gmail.com
SMTP_PORT=587                   # opcional, default: 587
```

## Dataset de prueba

URL usada para testing:

```
https://www.datos.gov.co/resource/ezzu-ke2k.csv
```

Contiene 472 filas y 10 columnas sobre jornadas de esterilización animal.
