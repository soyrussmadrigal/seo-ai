// src/app/components/HistoryTable.jsx
"use client";

import { useState } from "react";

export default function HistoryTable({ data }) {
  const [visibleCount, setVisibleCount] = useState(10);

  if (!data || data.length === 0) return null;

  const visibleData = data.slice(0, visibleCount);

  return (
    <div className="bg-[#161b22] rounded-xl shadow-lg overflow-hidden mt-6">
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm text-left text-white">
          <thead className="bg-[#010409] text-gray-300 text-xs uppercase tracking-wider">
            <tr>
              <th className="px-6 py-3 border-b border-gray-700">Keyword</th>
              <th className="px-6 py-3 border-b border-gray-700">Intent</th>
              <th className="px-6 py-3 border-b border-gray-700">Format</th>
              <th className="px-6 py-3 border-b border-gray-700">Clicks</th>
              <th className="px-6 py-3 border-b border-gray-700">
                Impressions
              </th>
              <th className="px-6 py-3 border-b border-gray-700">CTR</th>
              <th className="px-6 py-3 border-b border-gray-700">Position</th>
              <th className="px-6 py-3 border-b border-gray-700">Date</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {visibleData.map((item) => (
              <tr key={item.id} className="hover:bg-[#1a1f24] transition">
                <td className="px-6 py-4">{item.keyword}</td>
                <td className="px-6 py-4 capitalize">{item.intent}</td>
                <td className="px-6 py-4 capitalize">{item.format}</td>
                <td className="px-6 py-4">{item.clicks}</td>
                <td className="px-6 py-4">{item.impressions}</td>
                <td className="px-6 py-4">{item.ctr?.toFixed(2)}%</td>
                <td className="px-6 py-4">{item.position?.toFixed(2)}</td>
                <td className="px-6 py-4">
                  {/* Display the GSC date used for filtering */}
                  {new Date(item.gsc_date + "T00:00:00").toLocaleDateString(
                    "en-US"
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {visibleCount < data.length && (
        <div className="flex justify-center py-4">
          <button
            onClick={() => setVisibleCount((prev) => prev + 10)}
            className="bg-blue-700 hover:bg-blue-800 text-white font-semibold px-4 py-2 rounded transition"
          >
            Load more
          </button>
        </div>
      )}
    </div>
  );
}
