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

// Registro necesario para Chart.js
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
        console.error("❌ Error al cargar datos del gráfico:", err);
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
            <p className="text-gray-500">Cargando datos...</p>
          ) : chartData ? (
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
          ) : (
            <p className="text-red-500">No se encontraron datos.</p>
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
