"use client";

import { useState } from "react";

export default function ClassifyPage() {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleClassify = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/classify-pending", {
        method: "POST",
      });
      const result = await res.json();
      if (res.ok && result.status === "success") {
        setMessage(`✅ ${result.saved} keywords classified`);
      } else {
        setMessage("⚠️ No keywords classified or error occurred");
      }
    } catch (err) {
      setMessage("❌ Error classifying keywords");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="max-w-xl mx-auto px-6 py-12 text-white">
      <h1 className="text-2xl font-bold mb-4">Trigger Classification</h1>
      <button
        onClick={handleClassify}
        className="bg-purple-600 hover:bg-purple-700 px-6 py-2 rounded"
        disabled={loading}
      >
        {loading ? "Classifying..." : "Classify Pending Keywords"}
      </button>
      {message && <p className="mt-4 text-sm text-green-400">{message}</p>}
    </main>
  );
}
