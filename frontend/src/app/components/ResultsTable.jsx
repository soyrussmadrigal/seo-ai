"use client";

export default function ResultsTable({ data }) {
  if (!data || data.length === 0) return null;

  return (
    <div className="bg-[#161b22] rounded-xl shadow-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm text-left text-white">
          <thead className="bg-[#010409] text-gray-300 text-xs uppercase tracking-wider">
            <tr>
              <th className="px-6 py-3 border-b border-gray-700">Keyword</th>
              <th className="px-6 py-3 border-b border-gray-700">Intent</th>
              <th className="px-6 py-3 border-b border-gray-700">Recommended Format</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {data.map((item, idx) => (
              <tr key={idx} className="hover:bg-[#1a1f24] transition">
                <td className="px-6 py-4">{item.query}</td>
                <td className="px-6 py-4 capitalize">{item.intent}</td>
                <td className="px-6 py-4 capitalize">{item.recommended_format}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
