// src/components/FilterForm.jsx
"use client";

import { useState } from "react";
import DateRangePicker from "../components/DateRangePicker"; // Ajusta ruta si usás alias

export default function FilterForm({
  startDate,
  endDate,
  intent,
  format,
  setStartDate,
  setEndDate,
  setIntent,
  setFormat,
  applyFilters
}) {
  return (
    <form
      className="bg-[#161b22] p-4 rounded-lg mb-6 flex flex-wrap gap-4 items-end"
      onSubmit={(e) => {
        e.preventDefault();
        applyFilters(); // llama al fetch al hacer clic
      }}
    >
      <DateRangePicker
        startDate={startDate}
        endDate={endDate}
        onStartDateChange={setStartDate}
        onEndDateChange={setEndDate}
      />

      <div>
        <label className="block text-sm mb-1 text-white">Intent</label>
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
        <label className="block text-sm mb-1 text-white">Format</label>
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
  );
}
