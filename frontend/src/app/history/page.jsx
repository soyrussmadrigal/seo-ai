"use client";

import { useEffect, useState } from "react";
import HistoryTable from "../components/HistoryTable";
import { useHistoryStore } from "../store/historyStore";
import FilterForm from "../components/FilterForm";

export default function HistoryPage() {
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const { data, setData } = useHistoryStore();

  // Filtros
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [intent, setIntent] = useState("");
  const [format, setFormat] = useState("");

  const [filteredData, setFilteredData] = useState([]);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setMessage("");

      const res = await fetch("http://127.0.0.1:8000/history");
      const result = await res.json();

      if (Array.isArray(result)) {
        // Normaliza campos nulos por si el backend no los convierte
        const normalized = result.map((item) => ({
          ...item,
          intent: item.intent ?? "",
          format: item.format ?? "",
        }));

        setData(normalized);
        setFilteredData(normalized);
        window.historyData = normalized;
        console.log("History data:", normalized.slice(0, 5));
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

  const applyFilters = () => {
    console.log("🔎 Filtros aplicados con:", {
      startDate,
      endDate,
      intent,
      format,
    });

    const filtered = data.filter((item) => {
      const itemDate = new Date(item.gsc_date + "T00:00:00");

      const start = startDate ? new Date(startDate + "T00:00:00") : null;
      const end = endDate ? new Date(endDate + "T23:59:59") : null;

      return (
        (!start || itemDate >= start) &&
        (!end || itemDate <= end) &&
        (!intent || item.intent === intent) &&
        (!format || item.format === format)
      );
    });

    console.log("🎯 Resultados filtrados:", filtered.length);
    setFilteredData(filtered);
  };

  useEffect(() => {
    if (data.length === 0) fetchHistory();
    else {
      setFilteredData(data);
      setLoading(false);
    }
  }, []);

  return (
    <main className="max-w-6xl mx-auto px-6 py-12 text-white">
      <h1 className="text-3xl font-bold mb-6">Keyword History</h1>

      <FilterForm
        startDate={startDate}
        endDate={endDate}
        intent={intent}
        format={format}
        setStartDate={setStartDate}
        setEndDate={setEndDate}
        setIntent={setIntent}
        setFormat={setFormat}
        applyFilters={applyFilters}
      />

      {message && (
        <div className="bg-red-800 text-red-200 p-4 rounded mb-6">
          {message}
        </div>
      )}

      {loading ? (
        <p className="text-gray-400">Loading...</p>
      ) : (
        <HistoryTable data={filteredData} />
      )}
    </main>
  );
}
