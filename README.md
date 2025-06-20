# 🧠 SEO AI Assistant

Automated keyword classification using OpenAI and FastAPI — built to streamline search intent labeling and content format recommendation directly from Google Search Console queries.

> Created by **Rus Madrigal**

---

## 📌 What It Does

This tool helps SEO professionals classify search queries into:
- **Search intent**: `informational`, `transactional`, or `navigational`
- **Recommended format**: `article`, `tool`, `comparison`, `landing page`, `guide`, `FAQ`, or `other`

You can:
- 🔁 Process CSV files with GSC data
- ⚡ Use a local FastAPI endpoint for real-time classification
- 🧠 Scale and train smarter systems by integrating your own datasets

---

## ✨ Features

✅ AI-based classification using OpenAI  
✅ Realtime FastAPI endpoint (`/clasificar`)  
✅ `.env` secure config for keys  
✅ Designed for extensibility and clean UX  
✅ Ready to connect with Google Search Console API

---

## 🧰 Technologies

- Python 3.10+
- FastAPI
- OpenAI API (gpt-4-turbo or gpt-3.5-turbo)
- Pandas
- dotenv
- Uvicorn

---

## 📂 Project Structure

seo-ai-assistant/
│
├── data/
│ ├── gsc_keywords.csv # Input CSV with GSC queries
│ └── gsc_keywords_labeled.csv # Output with AI-labeled data
│
├── .env # API key (excluded from Git)
├── .gitignore # Prevents sensitive file commits
│
├── ai_labeler.py # Script for CSV classification
├── main.py # FastAPI app
├── requirements.txt # Python dependencies
└── README.md # Project documentation