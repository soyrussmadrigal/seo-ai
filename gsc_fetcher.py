import pandas as pd
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

# 1. Configuración
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
SERVICE_ACCOUNT_FILE = 'gsc_service_account.json'  # Asegúrate de tenerlo

# 2. Autenticación
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build('searchconsole', 'v1', credentials=credentials)

# 3. Propiedad (debe coincidir con cómo está en GSC)
site_url = "https://www.saldosimple.com/"  # ← CAMBIA ESTO si usás www o ruta distinta

# 4. Fechas (últimos 30 días)
end_date = datetime.today().date()
start_date = end_date - timedelta(days=30)

# 5. Consulta
request = {
    'startDate': start_date.isoformat(),
    'endDate': end_date.isoformat(),
    'dimensions': ['query', 'page'],
    'rowLimit': 1000
}

print(f"📡 Consultando GSC de {start_date} a {end_date} para {site_url}...")

response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()

# 6. Procesamiento
if 'rows' in response:
    rows = response['rows']
    data = []
    for row in rows:
        query = row['keys'][0]
        page = row['keys'][1]
        clicks = row.get('clicks', 0)
        impressions = row.get('impressions', 0)
        ctr = round(row.get('ctr', 0) * 100, 2)
        position = round(row.get('position', 0), 2)
        data.append([query, page, clicks, impressions, ctr, position])

    df = pd.DataFrame(data, columns=['query', 'page', 'clicks', 'impressions', 'ctr', 'position'])

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/gsc_keywords.csv", index=False)

    print(f"✅ {len(df)} filas guardadas en data/gsc_keywords.csv")
else:
    print("⚠️ No se encontraron datos para el periodo especificado.")
