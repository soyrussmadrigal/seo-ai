"use client";

import { useEffect, useState } from 'react';
import HistoryTable from '../components/HistoryTable';
import { useHistoryStore } from '../store/historyStore';

export default function HistoryPage() {
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const { data, setData } = useHistoryStore();

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/history");
        const result = await res.json();
        if (Array.isArray(result)) {
          setData(result);
        } else {
          setMessage("⚠️ Failed to load keyword history");
        }
      } catch (err) {
        console.error("❌ Failed to load keyword history", err);
        setMessage("❌ Error loading keyword history");
      } finally {
        setLoading(false);
      }
    };

    if (data.length === 0) {
      fetchHistory(); // solo si no está en cache
    } else {
      setLoading(false);
    }
  }, [data, setData]);

  return (
    <main className="max-w-6xl mx-auto px-6 py-12 text-white">
      <h1 className="text-3xl font-bold mb-4">Keyword History</h1>

      {message && (
        <div className="bg-red-800 text-red-200 p-4 rounded mb-6">
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
