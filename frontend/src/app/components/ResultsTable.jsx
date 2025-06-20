"use client";

import React from "react";

const ResultsTable = ({ data }) => {
  if (!data || data.length === 0) return null;

  return (
    <div className="bg-[#0d1117] p-6 rounded-2xl shadow-xl mt-8">
      <h2 className="text-white text-xl font-bold mb-4">Classification Results</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm text-left text-white border border-gray-700 rounded-md">
          <thead className="bg-[#010409] text-gray-300">
            <tr>
              <th className="px-4 py-3 border-b border-gray-700">Keyword</th>
              <th className="px-4 py-3 border-b border-gray-700">Intent</th>
              <th className="px-4 py-3 border-b border-gray-700">Recommended Format</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {data.map((item, idx) => (
              <tr key={idx} className="hover:bg-[#161b22] transition-colors">
                <td className="px-4 py-2">{item.query}</td>
                <td className="px-4 py-2 capitalize">{item.intent}</td>
                <td className="px-4 py-2 capitalize">{item.recommended_format}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ResultsTable;
