import React from "react";

export default function UrlCard({ url, summary, importance, reasoning }) {
  const safeSummary = Array.isArray(summary) ? summary : [];

  return (
    <div
      style={{
        border: "1px solid #ccc",
        padding: "12px",
        marginBottom: "12px",
        borderRadius: "6px",
      }}
    >
      <h3 style={{ wordBreak: "break-all" }}>{url}</h3>

      <p>
        <strong>Importance:</strong>{" "}
        <span
          style={{
            color:
              importance === "HIGH"
                ? "red"
                : importance === "MEDIUM"
                ? "orange"
                : "green",
          }}
        >
          {importance}
        </span>
      </p>

      {safeSummary.length > 0 ? (
        <ul>
          {safeSummary.map((s, i) => (
            <li key={i}>{s}</li>
          ))}
        </ul>
      ) : (
        <p style={{ color: "#777" }}>No meaningful changes detected.</p>
      )}

      {reasoning && (
        <p style={{ fontStyle: "italic", marginTop: "8px" }}>
          Reasoning: {reasoning}
        </p>
      )}
    </div>
  );
}
