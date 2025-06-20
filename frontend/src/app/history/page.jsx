"use client";

import { useEffect, useState } from 'react';
import HistoryTable from '../components/HistoryTable';
import { useHistoryStore } from '../store/historyStore';

export default function HistoryPage() {
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  const { data, setData } = useHistoryStore();

  useEffect(() => {
    const classifyAndLoad = async () => {
      if (data.length > 0) {
        setLoading(false); // ya está en cache
        return;
      }

      try {
        const res = await fetch("http://127.0.0.1:8000/classify-pending", {
          method: "POST",
        });
        const result = await res.json();

        if (res.ok && result.status === "success") {
          setMessage(`✅ ${result.saved} keywords classified successfully`);
        } else {
          setMessage("⚠️ No new keywords to classify or error occurred");
        }
      } catch (err) {
        console.error("❌ Error classifying pending keywords", err);
        setMessage("❌ Error classifying pending keywords");
      }

      try {
        const histRes = await fetch("http://127.0.0.1:8000/history");
        const histData = await histRes.json();
        if (Array.isArray(histData)) {
          setData(histData); // guarda en zustand
        }
      } catch (err) {
        console.error("❌ Failed to load keyword history", err);
      } finally {
        setLoading(false);
      }
    };

    classifyAndLoad();
  }, [data, setData]);

  return (
    <main className="max-w-6xl mx-auto px-6 py-12 text-white">
      <h1 className="text-3xl font-bold mb-4">Keyword History</h1>

      {message && (
        <div className="bg-green-900 text-green-300 p-4 rounded mb-6">
          {message}
        </div>
      )}

      {loading ? (
        <p className="text-gray-400">Loading...</p>
      ) : (
        <HistoryTable data={data} />
      )}
    </main>
  );
}
