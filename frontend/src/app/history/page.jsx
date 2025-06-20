"use client";

import { useEffect, useState } from "react";
import HistoryTable from "../components/HistoryTable";

export default function HistoryPage() {
  const [allData, setAllData] = useState([]);      // Todo el historial
  const [displayedData, setDisplayedData] = useState([]); // Solo lo que se muestra
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [loadingMore, setLoadingMore] = useState(false);
  const [itemsToShow, setItemsToShow] = useState(10); // Inicial: 10

  const loadHistory = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/history");
      const json = await res.json();
      if (Array.isArray(json)) {
        setAllData(json);
        setDisplayedData(json.slice(0, itemsToShow));
      }
    } catch (err) {
      console.error("❌ Error loading history", err);
      setMessage("❌ Error loading history");
    }
  };

  const classifyPending = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/classify-pending", {
        method: "POST",
      });
      const result = await res.json();

      if (res.ok && result.status === "success") {
        setMessage(`✅ ${result.saved} keywords classified`);
      } else {
        setMessage("⚠️ No more keywords to classify");
      }
    } catch (err) {
      console.error("❌ Error classifying keywords", err);
      setMessage("❌ Error classifying keywords");
    }
  };

  useEffect(() => {
    const init = async () => {
      await classifyPending(); // solo 10
      await loadHistory();
      setLoading(false);
    };
    init();
  }, []);

  const handleLoadMore = async () => {
    setLoadingMore(true);
    await classifyPending(); // Clasifica 10 más
    await loadHistory();     // Refresca datos
    setItemsToShow((prev) => prev + 10); // Aumenta el rango
    setLoadingMore(false);
  };

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
        <>
          <HistoryTable data={displayedData} />
          {displayedData.length < allData.length && (
            <div className="flex justify-center mt-6">
              <button
                onClick={handleLoadMore}
                disabled={loadingMore}
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold px-4 py-2 rounded"
              >
                {loadingMore ? "Loading more..." : "Classify & Load More"}
              </button>
            </div>
          )}
        </>
      )}
    </main>
  );
}
