from datetime import datetime
from app.models import KeywordHistory
from app.database import SessionLocal
from app.gsc_fetcher import extraer_datos_gsc as fetch_gsc_data
import os
import sys
import dotenv

# 👇 Asegura que el path raíz esté incluido
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), ".")))


dotenv.load_dotenv()


def save_keywords(days=30):
    data = fetch_gsc_data(days)
    db = SessionLocal()
    inserted = 0
    skipped = 0

    for row in data:
        exists = db.query(KeywordHistory).filter_by(
            keyword=row["keyword"],
            gsc_date=row["date"]
        ).first()

        if exists:
            skipped += 1
            continue

       keyword_entry = KeywordHistory(
    keyword=row["keyword"],
    clicks=row["clicks"],
    impressions=row["impressions"],
    ctr=row["ctr"],
    position=row["position"],
    gsc_date=datetime.strptime(row["date"], "%Y-%m-%d").date(),
    intent=row.get("intent", ""),   # ← asegura que sea string
    format=row.get("format", "")    # ← asegura que sea string
)
        db.add(keyword_entry)
        inserted += 1

    db.commit()
    db.close()

    print(f"✅ Inserted: {inserted}")
    print(f"⏭️ Skipped (already exists): {skipped}")

if __name__ == "__main__":
    save_keywords(days=30)
