"use client";

import { Dialog } from "@headlessui/react";
import { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend
);

export default function KeywordChartModal({ keyword, onClose }) {
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [recommendation, setRecommendation] = useState(null);

  // Helper to calculate if there's a downward trend in position
  function detectDownwardTrend(position = []) {
    let drops = 0;
    let rises = 0;
    for (let i = 1; i < position.length; i++) {
      if (position[i] > position[i - 1]) {
        drops++;
      } else if (position[i] < position[i - 1]) {
        rises++;
      }
    }
    return { drops, rises };
  }

  // Generate dynamic recommendation based on trend analysis
  function getRecommendation(position, ctr, clicks) {
    if (position.length < 3) return null;

    const { drops, rises } = detectDownwardTrend(position);
    const last = position[position.length - 1];
    const first = position[0];
    const ctrNow = ctr[ctr.length - 1];
    const ctrBefore = ctr[0];
    const clicksNow = clicks[clicks.length - 1];
    const clicksBefore = clicks[0];

    // Rule 1: Overall ranking trend is declining
    if (drops > rises && last > first) {
      return `⚠️ Your ranking has declined during this period. Consider refreshing your content, adding internal links, or checking competitors for this keyword.`;
    }

    // Rule 2: High impressions but low CTR
    if (ctrNow < 1 && clicksNow < clicksBefore) {
      return `📉 You're getting visibility but not enough clicks. Consider improving your title or meta description with more compelling CTAs.`;
    }

    // Rule 3: Position stable, CTR consistently low
    if (Math.abs(last - first) < 1 && ctrNow < 2) {
      return `ℹ️ Your position is stable but CTR is low. Try testing different hooks in your meta title or using emojis/rich snippets.`;
    }

    return null;
  }

  useEffect(() => {
    const fetchKeywordData = async () => {
      try {
        const res = await fetch(
          `http://127.0.0.1:8000/history/keyword?text=${encodeURIComponent(
            keyword
          )}`
        );
        const json = await res.json();

        const labels = json.map((item) => item.gsc_date);
        const position = json.map((item) => item.position);
        const clicks = json.map((item) => item.clicks);
        const ctr = json.map((item) => item.ctr);

        const rec = getRecommendation(position, ctr, clicks);
        setRecommendation(rec);

        setChartData({
          labels,
          datasets: [
            {
              label: "Position",
              data: position,
              yAxisID: "yPosition",
              borderWidth: 2,
              borderColor: "#3b82f6",
              backgroundColor: "rgba(59, 130, 246, 0.1)",
            },
            {
              label: "Clicks",
              data: clicks,
              yAxisID: "y",
              borderWidth: 2,
              borderColor: "#10b981",
              backgroundColor: "rgba(16, 185, 129, 0.1)",
            },
            {
              label: "CTR",
              data: ctr,
              yAxisID: "y",
              borderWidth: 2,
              borderColor: "#f59e0b",
              backgroundColor: "rgba(245, 158, 11, 0.1)",
            },
          ],
        });
      } catch (err) {
        console.error("❌ Error loading chart data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchKeywordData();
  }, [keyword]);

  return (
    <Dialog open={true} onClose={onClose} className="relative z-50">
      <div className="fixed inset-0 bg-black/60" aria-hidden="true" />
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="bg-white max-w-3xl w-full rounded-xl p-6 shadow-xl">
          <Dialog.Title className="text-xl font-semibold mb-4">
            <span className="text-blue-600">{keyword}</span>
          </Dialog.Title>

          {loading ? (
            <p className="text-gray-500">Loading data...</p>
          ) : chartData ? (
            <>
              <Line
                data={chartData}
                options={{
                  responsive: true,
                  scales: {
                    y: {
                      beginAtZero: false,
                    },
                    yPosition: {
                      position: "left",
                      reverse: true,
                      title: {
                        display: true,
                        text: "Position",
                      },
                    },
                  },
                }}
              />
              {recommendation ? (
                <div className="mt-6 p-4 bg-yellow-100 text-yellow-800 rounded text-sm">
                  <strong>SEO insight:</strong>
                  <br />
                  {recommendation}
                </div>
              ) : (
                <div className="mt-6 p-4 text-sm text-gray-500">
                  No SEO insight available based on current trend.
                </div>
              )}
            </>
          ) : (
            <p className="text-red-500">No data found.</p>
          )}

          <div className="mt-6 flex justify-end">
            <button
              onClick={onClose}
              className="bg-gray-800 text-white px-4 py-2 rounded hover:bg-gray-700"
            >
              Close
            </button>
          </div>
        </Dialog.Panel>
      </div>
    </Dialog>
  );
}
