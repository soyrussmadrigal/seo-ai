# app/gsc_fetcher.py

from datetime import date, timedelta
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Environment variables
SERVICE_ACCOUNT_FILE = os.getenv("GSC_SERVICE_ACCOUNT_FILE")
SITE_URL = os.getenv("GSC_SITE_URL")


def extraer_datos_gsc(days: int = 30):
    """
    Fetches data from Google Search Console for the last `days` days (including today).
    Returns a list of dictionaries with: keyword, date, clicks, impressions, ctr, position.
    """
    if not SERVICE_ACCOUNT_FILE or not SITE_URL:
        raise ValueError(
            "Missing GSC_SERVICE_ACCOUNT_FILE or GSC_SITE_URL in environment variables.")

    # Authenticate with the service account
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
    )
    service = build("searchconsole", "v1", credentials=creds)

    # Date range
    today = date.today()
    start = (today - timedelta(days=days - 1)).isoformat()
    end = today.isoformat()

    # Query Search Console API
    body = {
        "startDate": start,
        "endDate": end,
        "dimensions": ["query", "date"],
        "rowLimit": 25000
    }

    response = service.searchanalytics().query(
        siteUrl=SITE_URL, body=body).execute()

    # Format response
    data = []
    for row in response.get("rows", []):
        query, row_date = row.get("keys", ["", ""])
        data.append({
            "keyword": query,
            "date": row_date,
            "clicks": row.get("clicks", 0),
            "impressions": row.get("impressions", 0),
            "ctr": row.get("ctr", 0.0),
            "position": row.get("position", 0.0),
        })

    return data
