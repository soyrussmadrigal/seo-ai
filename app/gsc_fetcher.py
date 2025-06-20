# app/gsc_fetcher.py
import pandas as pd
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

def extraer_datos_gsc(site_url="https://www.saldosimple.com/"):
    SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
    SERVICE_ACCOUNT_FILE = 'gsc_service_account.json'

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('searchconsole', 'v1', credentials=credentials)

    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=30)

    request = {
        'startDate': start_date.isoformat(),
        'endDate': end_date.isoformat(),
        'dimensions': ['query', 'page'],
        'rowLimit': 1000
    }

    response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()

    if 'rows' in response:
        data = []
        for row in response['rows']:
            query, page = row['keys']
            clicks = row.get('clicks', 0)
            impressions = row.get('impressions', 0)
            ctr = round(row.get('ctr', 0) * 100, 2)
            position = round(row.get('position', 0), 2)
            data.append({
                'query': query,
                'page': page,
                'clicks': clicks,
                'impressions': impressions,
                'ctr': ctr,
                'position': position
            })

        df = pd.DataFrame(data)
        os.makedirs("data", exist_ok=True)
        df.to_csv("data/gsc_keywords.csv", index=False)
        return data
    else:
        return []
