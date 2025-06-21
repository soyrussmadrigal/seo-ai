// src/components/DateRangePicker.jsx
"use client";

import React from "react";

export default function DateRangePicker({ startDate, endDate, onStartDateChange, onEndDateChange }) {
  return (
    <div className="flex gap-4">
      <div>
        <label className="block text-sm mb-1 text-white">Start Date</label>
        <input
          type="date"
          value={startDate}
          onChange={(e) => onStartDateChange(e.target.value)}
          className="bg-gray-800 text-white rounded px-3 py-1"
        />
      </div>

      <div>
        <label className="block text-sm mb-1 text-white">End Date</label>
        <input
          type="date"
          value={endDate}
          onChange={(e) => onEndDateChange(e.target.value)}
          className="bg-gray-800 text-white rounded px-3 py-1"
        />
      </div>
    </div>
  );
}
