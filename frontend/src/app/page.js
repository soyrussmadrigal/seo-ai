"use client";

import { useState } from "react";
import ResultsTable from "./components/ResultsTable";

export default function Home() {
  const [keywords, setKeywords] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleClassify = async () => {
    setLoading(true);
    try {
      // Clasificación con FastAPI
      const res = await fetch("http://127.0.0.1:8000/clasificar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          keywords: keywords.split("\n").filter(Boolean),
        }),
      });

      const data = await res.json();
      setResults(data);

      // Guardar historial en FastAPI
      await fetch("http://127.0.0.1:8000/save_history", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(
          data.map((item) => ({
            keyword: item.keyword,
            intent: item.intent,
            format: item.format,
            clicks: item.clicks || 0,
            impressions: item.impressions || 0,
            ctr: item.ctr || 0,
            position: item.position || 0,
          }))
        ),
      });
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="max-w-4xl mx-auto py-16 px-6 min-h-screen bg-[#0d1117] text-white">
      <div className="text-center mb-10">
        <h1 className="text-4xl font-extrabold tracking-tight mb-2 flex justify-center items-center gap-2">
          <span className="text-indigo-400">🔎</span> SEO Intent Classifier
        </h1>
        <p className="text-gray-400 text-sm">
          Analyze search intent and get smart content recommendations
        </p>
      </div>

      <div className="bg-[#161b22] p-6 rounded-xl shadow-md">
        <label htmlFor="keywords" className="block text-sm font-medium mb-2">
          Enter one keyword per line:
        </label>
        <textarea
          id="keywords"
          className="w-full h-40 p-4 rounded-md border border-gray-600 bg-[#0d1117] text-white placeholder-gray-400 focus:ring-2 focus:ring-indigo-500 focus:outline-none transition resize-none"
          placeholder="e.g.\nbest credit cards\nhow to improve SEO\ncar insurance simulator"
          value={keywords}
          onChange={(e) => setKeywords(e.target.value)}
        />

        <button
          onClick={handleClassify}
          className="mt-4 w-full sm:w-auto bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-2 rounded-lg font-medium transition disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={loading}
        >
          {loading ? "Classifying..." : "Classify Keywords"}
        </button>
      </div>

      {results.length > 0 && (
        <section className="mt-12">
          <h2 className="text-2xl font-bold mb-4">Classification Results</h2>
          <ResultsTable data={results} />
        </section>
      )}
    </main>
  );
}
