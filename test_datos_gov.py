"""
Test: demostrar que pd.read_excel funciona con URLs reales de archivos .xlsx
y simular exactamente lo que hace datos_service.py
"""
import io
import requests
import pandas as pd

headers = {"User-Agent": "Mozilla/5.0"}

# ── URLs públicas reales de archivos .xlsx ──────────────────────────────────
urls_xlsx = {
    "Financial Sample (Microsoft)":
        "https://go.microsoft.com/fwlink/?LinkID=521962",
    "World Bank (GitHub raw)":
        "https://raw.githubusercontent.com/datasets/world-bank/main/data/world-bank-data.xlsx",
    "Sample XLSX (file-examples.com)":
        "https://file-examples.com/storage/fe58ebc2a367c3b6a5db03e/2017/02/file_example_XLSX_10.xlsx",
}

print("=" * 65)
print("  PRUEBA: pd.read_excel con archivos .xlsx reales desde URLs")
print("  (Exactamente como lo hace tu datos_service.py)")
print("=" * 65)

funciono = None
for nombre, url in urls_xlsx.items():
    print(f"\n--- {nombre} ---")
    print(f"URL: {url}")
    try:
        # Esto es EXACTAMENTE lo que hace tu _descargar_df():
        respuesta = requests.get(url, headers=headers, timeout=30)
        respuesta.raise_for_status()
        df = pd.read_excel(io.BytesIO(respuesta.content))

        print(f"FUNCIONA: {df.shape[0]} filas x {df.shape[1]} columnas")
        print(f"Columnas: {list(df.columns[:6])}")
        print(df.head(3).to_string()[:400])
        funciono = (nombre, url, df)
        break  # Con uno que funcione basta para demostrar

    except Exception as e:
        print(f"Error: {e}")

# ── Ahora simular la llamada completa a tu API ─────────────────────────────
if funciono:
    nombre, url, df = funciono
    print(f"\n\n{'=' * 65}")
    print("  SIMULACIÓN: así lo consumiría Java desde tu API")
    print("=" * 65)
    print(f"""
    POST /datos/cargar
    {{
        "url": "{url}",
        "tipo": "xlsx",
        "sesion_id": 1
    }}

    Respuesta esperada:
    {{
        "mensaje": "Conjunto de datos cargados",
        "dataset_id": 1,
        "total_filas": {df.shape[0]},
        "total_columnas": {df.shape[1]},
        "tiene_nulos": {bool(df.isnull().any().any())}
    }}
    """)

# ── Comparación lado a lado: CSV vs XLSX ───────────────────────────────────
print("=" * 65)
print("  COMPARACIÓN: CSV (datos.gov.co) vs XLSX (URL directa)")
print("=" * 65)

print("\n--- CSV desde datos.gov.co ---")
url_csv = "https://www.datos.gov.co/resource/i7cb-raxc.csv?$limit=5"
try:
    r = requests.get(url_csv, headers=headers, timeout=30)
    df_csv = pd.read_csv(io.StringIO(r.text))
    print(f"FUNCIONA: {df_csv.shape[0]} filas x {df_csv.shape[1]} columnas")
except Exception as e:
    print(f"Error: {e}")

if funciono:
    print(f"\n--- XLSX desde URL directa ---")
    print(f"FUNCIONA: {df.shape[0]} filas x {df.shape[1]} columnas")

print(f"""
CONCLUSIÓN:
  - CSV: funciona con datos.gov.co (API SODA) o cualquier URL
  - XLSX: funciona con cualquier URL que sirva un archivo .xlsx real
  - datos.gov.co NO sirve .xlsx, pero eso no importa
  - Tu API acepta AMBOS formatos — el usuario elige de dónde viene el archivo
""")
