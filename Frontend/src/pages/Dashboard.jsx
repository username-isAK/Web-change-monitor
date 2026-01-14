import React, { useState, useEffect } from "react";
import UrlCard from "../components/UrlCard";
import axios from "axios";

export default function App() {
  const [urlsInput, setUrlsInput] = useState("");
  const [urls, setUrls] = useState([]); // All registered URLs
  const [results, setResults] = useState([]); // Summaries
  const [loading, setLoading] = useState(false);
  const userEmail = "user@example.com";
  const API_BASE = "/api";

  const fetchUrls = async () => {
    try {
      const res = await axios.get(`${API_BASE}/urls`, {
        headers: { "user-email": userEmail },
      });
      setUrls(res.data);
    } catch (err) {
      console.error("Failed to fetch URLs:", err);
    }
  };

  const handleDelete = async (urlId) => {
    try {
      await axios.delete(`${API_BASE}/urls/${urlId}`, {
        headers: { "user-email": userEmail },
      });
      fetchUrls();
      fetchSummaries();
    } catch (err) {
      console.error("Failed to delete URL:", err);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const newUrls = urlsInput
        .split("\n")
        .map((u) => u.trim())
        .filter(Boolean);

      for (const url of newUrls) {
        try {
          await axios.post(
            `${API_BASE}/urls`,
            { url },
            { headers: { "user-email": userEmail } }
          );
        } catch (err) {
          console.error("Failed to register URL:", url, err);
        }
      }

      setUrlsInput("");
      fetchUrls();
      fetchSummaries();
    } finally {
      setLoading(false);
    }
  };

  const fetchSummaries = async () => {
    try {
      const res = await axios.get(`${API_BASE}/summaries`, {
        headers: { "user-email": userEmail },
      });
      setResults(res.data.results ?? []);
    } catch (err) {
      console.error("Failed to fetch summaries:", err);
    }
  };

  useEffect(() => {
    fetchUrls();
    fetchSummaries();
    const interval = setInterval(() => {
      fetchSummaries();
      fetchUrls();
    }, 30000); // refresh every 30s
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: "20px" }}>
      <h2>Web Change Monitor</h2>

      <div style={{ marginBottom: "20px" }}>
        <h3>Register new URLs</h3>
        <textarea
          rows={5}
          value={urlsInput}
          onChange={(e) => setUrlsInput(e.target.value)}
          placeholder="Enter one URL per line"
          style={{ width: "100%", marginBottom: "12px" }}
        />
        <button onClick={handleSubmit}>Register URLs</button>
      </div>

      <div style={{ marginBottom: "20px" }}>
        <h3>Registered URLs</h3>
        {urls.length === 0 && <p>No URLs registered yet.</p>}
        {urls.map((u) => (
          <div
            key={u.id}
            style={{
              border: "1px solid #ccc",
              padding: "12px",
              marginBottom: "12px",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <span>{u.url}</span>
            <div>
              <span
                style={{
                  color: "white",
                  backgroundColor: "green",
                  padding: "2px 6px",
                  borderRadius: "4px",
                  marginRight: "8px",
                  fontSize: "12px",
                }}
              >
                Monitoring
              </span>
              <button onClick={() => handleDelete(u.id)}>Stop</button>
            </div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: "20px" }}>
        <h3>Summaries</h3>
        {loading && <p>Loading summaries...</p>}
        {results.map((r, idx) => (
          <UrlCard
            key={idx}
            url={r.url}
            summary={r.summary}
            importance={r.importance}
            reasoning={r.reasoning}
          />
        ))}
      </div>
    </div>
  );
}
