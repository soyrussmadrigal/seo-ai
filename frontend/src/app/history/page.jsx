"use client";

import { useEffect, useState } from "react";
import HistoryTable from "../components/HistoryTable";
import { useHistoryStore } from "../store/historyStore";


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
        setData(result);
        setFilteredData(result); // Inicial sin filtros
        console.log("History data:", result.slice(0, 5));
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
    let filtered = data;

    if (startDate) {
      filtered = filtered.filter(item => {
        const date = new Date(item.gsc_date);
        return date >= new Date(startDate);
      });
    }

    if (endDate) {
      filtered = filtered.filter(item => {
        const date = new Date(item.gsc_date);
        return date <= new Date(endDate);
      });
    }

    if (intent) {
      filtered = filtered.filter(item => item.intent === intent);
    }

    if (format) {
      filtered = filtered.filter(item => item.format === format);
    }

    setFilteredData(filtered);
  };

  useEffect(() => {
    if (data.length === 0) fetchHistory();
    else {
      setFilteredData(data); // si ya estaba cargado en Zustand
      setLoading(false);
    }
  }, []);

  return (
    <main className="max-w-6xl mx-auto px-6 py-12 text-white">
      <h1 className="text-3xl font-bold mb-6">Keyword History</h1>

      {/* 🎯 Filtros */}
      <form
        className="bg-[#161b22] p-4 rounded-lg mb-6 flex flex-wrap gap-4 items-end"
        onSubmit={(e) => {
          e.preventDefault();
          applyFilters();
        }}
      >
        <div>
          <label className="block text-sm mb-1">Start Date</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="bg-gray-800 text-white rounded px-3 py-1"
          />
        </div>

        <div>
          <label className="block text-sm mb-1">End Date</label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="bg-gray-800 text-white rounded px-3 py-1"
          />
        </div>

        <div>
          <label className="block text-sm mb-1">Intent</label>
          <select
            value={intent}
            onChange={(e) => setIntent(e.target.value)}
            className="bg-gray-800 text-white rounded px-3 py-1"
          >
            <option value="">All</option>
            <option value="informational">Informational</option>
            <option value="transactional">Transactional</option>
            <option value="navigational">Navigational</option>
          </select>
        </div>

        <div>
          <label className="block text-sm mb-1">Format</label>
          <select
            value={format}
            onChange={(e) => setFormat(e.target.value)}
            className="bg-gray-800 text-white rounded px-3 py-1"
          >
            <option value="">All</option>
            <option value="article">Article</option>
            <option value="tool">Tool</option>
            <option value="comparator">Comparator</option>
            <option value="landing page">Landing Page</option>
            <option value="guide">Guide</option>
            <option value="FAQ">FAQ</option>
            <option value="other">Other</option>
          </select>
        </div>

        <button
          type="submit"
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
        >
          Apply Filters
        </button>
      </form>

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
