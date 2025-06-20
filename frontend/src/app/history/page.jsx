'use client';

import { useEffect, useState } from 'react';
import HistoryTable from '../components/HistoryTable';

export default function HistoryPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  useEffect(() => {
    const loadData = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/history");
        const rawText = await res.text();
        console.log("📦 Raw response:", rawText);

        const parsed = JSON.parse(rawText);

        if (Array.isArray(parsed)) {
          setData(parsed);
          setMessage(`✅ ${parsed.length} keywords loaded`);
        } else {
          setMessage("⚠️ Could not load history data");
          console.warn("⚠️ Unexpected response:", parsed);
        }
      } catch (err) {
        console.error("❌ Error loading history:", err);
        setMessage("❌ Error loading history");
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

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
