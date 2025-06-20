// app/page.jsx
'use client'

import { useState } from 'react'

export default function Home() {
  const [keywords, setKeywords] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)

  const handleClassify = async () => {
    setLoading(true)
    try {
      const res = await fetch('http://127.0.0.1:8000/clasificar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keywords: keywords.split('\n').filter(Boolean) }),
      })

      const data = await res.json()
      setResults(data)
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="max-w-3xl mx-auto py-12 px-6">
      <h1 className="text-3xl font-bold mb-4">🔍 SEO Intent Classifier</h1>

      <textarea
        className="w-full h-40 p-4 border rounded-md shadow mb-4 resize-none"
        placeholder="Enter one keyword per line..."
        value={keywords}
        onChange={(e) => setKeywords(e.target.value)}
      />

      <button
        onClick={handleClassify}
        className="bg-black text-white px-6 py-2 rounded hover:bg-gray-800 transition"
        disabled={loading}
      >
        {loading ? 'Classifying...' : 'Classify Keywords'}
      </button>

      {results.length > 0 && (
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-2">Results</h2>
          <table className="w-full text-left border border-gray-300">
            <thead className="bg-gray-100">
              <tr>
                <th className="p-2 border">Keyword</th>
                <th className="p-2 border">Intent</th>
                <th className="p-2 border">Format</th>
              </tr>
            </thead>
            <tbody>
              {results.map((item, index) => (
                <tr key={index} className="border-t">
                  <td className="p-2 border">{item.query}</td>
                  <td className="p-2 border">{item.intent}</td>
                  <td className="p-2 border">{item.recommended_format}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  )
}
