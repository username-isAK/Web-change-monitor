import React, { useState, useEffect } from "react";
import axios from "axios";

export default function UrlCard({ url, summary, importance, reasoning }) {
  const safeSummary = Array.isArray(summary) ? summary : [];

  const importanceStyles = {
    HIGH: "bg-red-50 border-red-200 text-red-700",
    MEDIUM: "bg-amber-50 border-amber-200 text-amber-700",
    LOW: "bg-emerald-50 border-emerald-200 text-emerald-700"
  };

  const importanceIcons = {
    HIGH: "🔴",
    MEDIUM: "🟡",
    LOW: "🟢"
  };

  return (
    <div className="group bg-white border border-gray-200 rounded-xl p-6 mb-4 shadow-sm hover:shadow-md transition-all duration-300">
      <div className="flex items-start justify-between mb-4">
        <h3 className="font-semibold text-gray-800 break-all flex-1">{url}</h3>
      </div>

      <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium mb-4 border ${importanceStyles[importance] || importanceStyles.LOW}`}>
        <span>{importanceIcons[importance] || importanceIcons.LOW}</span>
        <span>{importance}</span>
      </div>

      {safeSummary.length > 0 ? (
        <ul className="space-y-2 mb-4">
          {safeSummary.map((s, i) => (
            <li key={i} className="flex items-start gap-2 text-gray-700">
              <span className="text-blue-500 mt-1.5">•</span>
              <span className="flex-1">{s}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-gray-400 italic">No meaningful changes detected.</p>
      )}

      {reasoning && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          <p className="text-sm text-gray-600">
            <span className="font-medium">Reasoning:</span> {reasoning}
          </p>
        </div>
      )}
    </div>
  );
}