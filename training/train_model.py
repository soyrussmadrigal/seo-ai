# training/train_model.py

import os
import argparse
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import KeywordHistory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import joblib

def get_labeled_data(db: Session, target_field: str):
    return db.query(KeywordHistory).filter(
        getattr(KeywordHistory, target_field).isnot(None),
        getattr(KeywordHistory, target_field) != ""
    ).all()

def train_model(data, target_field: str, output_path: str):
    queries = [row.keyword for row in data]
    labels = [getattr(row, target_field) for row in data]

    X_train, X_test, y_train, y_test = train_test_split(queries, labels, test_size=0.2, random_state=42)

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('clf', LogisticRegression(max_iter=1000))
    ])

    pipeline.fit(X_train, y_train)
    accuracy = pipeline.score(X_test, y_test)
    print(f"✅ Accuracy del modelo para '{target_field}': {accuracy:.2f}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    joblib.dump(pipeline, output_path)
    print(f"📦 Modelo guardado en: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Entrenamiento de modelos SEO IA")
    parser.add_argument("--target", choices=["intent", "format"], required=True, help="Campo a predecir: 'intent' o 'format'")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        data = get_labeled_data(db, args.target)
        if not data:
            print(f"⚠️ No hay datos etiquetados para '{args.target}'.")
            return
        output_path = f"models/{args.target}_classifier.pkl"
        train_model(data, args.target, output_path)
    finally:
        db.close()

if __name__ == "__main__":
    main()
