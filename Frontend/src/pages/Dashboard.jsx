import React, { useState, useEffect } from "react";
import UrlCard from "../components/UrlCard";
import axios from "axios";

export default function App() {
  const [urlsInput, setUrlsInput] = useState("");
  const [urls, setUrls] = useState([]);
  const [results, setResults] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  const [userEmail, setUserEmail] = useState(() => {
    return localStorage.getItem("userEmail") || "";
  });
  const [emailInput, setEmailInput] = useState("");

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

  const fetchSummaries = async () => {
    try {
      const res = await axios.get(`${API_BASE}/summaries`, {
        headers: { "user-email": userEmail },
      });
      setResults(res.data ?? []);
    } catch (err) {
      console.error("Failed to fetch summaries:", err);
    }
  };

  const showBrowserNotification = (notification) => {
    if (Notification.permission !== "granted") return;

    new Notification("Website Change Detected", {
      body: notification.message,
      tag: `url-${notification.id}`,
    });
  };

  const fetchNotifications = async () => {
    try {
      const res = await axios.get(`${API_BASE}/notifications`, {
        headers: { "user-email": userEmail },
      });

      const newNotifications = res.data || [];

      newNotifications.forEach((n) => {
        const alreadyExists = notifications.find((x) => x.id === n.id);
        if (!alreadyExists && !n.read) {
          showBrowserNotification(n);
        }
      });

      setNotifications(newNotifications);
    } catch (err) {
      console.error("Failed to fetch notifications:", err);
    }
  };

  const deleteNotification = async (id) => {
    try {
      await axios.delete(`${API_BASE}/notifications/${id}`, {
        headers: { "user-email": userEmail },
      });
      fetchNotifications();
    } catch (err) {
      console.error("Failed to delete notification:", err);
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
        await axios.post(
          `${API_BASE}/urls`,
          { url },
          { headers: { "user-email": userEmail } }
        );
      }

      setUrlsInput("");
      fetchUrls();
      fetchSummaries();
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!userEmail) return;

    fetchUrls();
    fetchSummaries();
    fetchNotifications();

    if ("Notification" in window && Notification.permission === "default") {
      Notification.requestPermission();
    }

    const interval = setInterval(() => {
      fetchUrls();
      fetchSummaries();
      fetchNotifications();
    }, 5 * 60 * 1000);

    return () => clearInterval(interval);
  }, [userEmail]);

  const unreadCount = notifications.filter((n) => !n.read).length;

  if (!userEmail) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
        <div className="absolute inset-0 opacity-5 bg-[radial-gradient(#444cf7_1px,transparent_1px)] [background-size:16px_16px]"></div>

        <div className="relative bg-white/80 backdrop-blur-xl p-8 rounded-2xl shadow-2xl w-full max-w-md border border-white/20">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl mb-4 shadow-lg">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </div>
            <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-2">
              Web Change Monitor
            </h2>
            <p className="text-gray-600">Track changes across the web, effortlessly</p>
          </div>

          <input
            type="email"
            placeholder="you@example.com"
            value={emailInput}
            onChange={(e) => setEmailInput(e.target.value)}
            className="w-full border border-gray-200 rounded-xl px-4 py-3 mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
          />

          <button
            onClick={() => {
              if (!emailInput) return;
              localStorage.setItem("userEmail", emailInput);
              setUserEmail(emailInput);
            }}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 rounded-xl font-medium hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
          >
            Continue
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50/30 p-6">
      <div className="max-w-5xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              Web Change Monitor
            </h2>
            <p className="text-gray-600 mt-1">Stay updated with real-time web changes</p>
          </div>
          <div className="relative flex items-center gap-4">
          <button
            onClick={() => setShowNotifications((p) => !p)}
            className="relative p-2 rounded-lg hover:bg-gray-100 transition"
          >
            🔔
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 bg-red-600 text-white text-xs rounded-full px-1.5">
                {unreadCount}
              </span>
            )}
          </button>

          {/* Dropdown */}
          {showNotifications && (
            <div className="absolute right-0 top-12 w-96 bg-white rounded-xl shadow-xl border z-50">
              <div className="p-3 border-b font-semibold">
                Notifications
              </div>

              {notifications.length === 0 && (
                <p className="p-4 text-sm text-gray-500">No notifications</p>
              )}

              <div className="max-h-80 overflow-y-auto">
                {notifications.map((n) => (
                  <div
                    key={n.id}
                    className={`p-3 border-b text-sm ${
                      n.read ? "bg-gray-50" : "bg-yellow-50"
                    }`}
                  >
                    <div className="font-medium">
                      {n.importance.toUpperCase()}
                    </div>

                    <p className="my-1">{n.message}</p>

                    <small className="text-gray-500 break-all">
                      {n.url}
                    </small>

                    <div className="text-right mt-2">
                      <button
                        onClick={() => deleteNotification(n.id)}
                        className="text-red-600 text-xs hover:underline"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <button
            onClick={() => {
              localStorage.removeItem("userEmail");
              setUserEmail("");
            }}
            className="text-sm text-gray-600 hover:text-red-600 transition px-4 py-2 rounded-lg hover:bg-red-50"
          >
            Switch User
          </button>
        </div>

        </div>

        <div className="bg-white rounded-2xl shadow-lg p-6 mb-8 border border-gray-100">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">Register New URLs</h3>
          <textarea
            rows={5}
            value={urlsInput}
            onChange={(e) => setUrlsInput(e.target.value)}
            placeholder="Enter one URL per line&#10;https://example.com&#10;https://another-site.com"
            className="w-full border border-gray-200 rounded-xl p-4 mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition resize-none font-mono text-sm"
          />
          <button
            onClick={handleSubmit}
            disabled={loading || !urlsInput.trim()}
            className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white px-6 py-3 rounded-xl font-medium hover:from-emerald-700 hover:to-teal-700 transition-all duration-300 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transform hover:-translate-y-0.5"
          >
            {loading ? "Registering..." : "Register URLs"}
          </button>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-6 mb-8 border border-gray-100">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">
            Registered URLs ({urls.length})
          </h3>

          {urls.length === 0 && (
            <div className="text-center py-8">
              <svg className="w-16 h-16 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
              <p className="text-gray-400">No URLs registered yet</p>
            </div>
          )}

          <div className="space-y-3">
            {urls.map((u) => (
              <div
                key={u.id}
                className="border border-gray-200 rounded-xl p-4 flex justify-between items-center hover:border-blue-300 hover:shadow-sm transition-all duration-200 group"
              >
                <div className="flex-1">
                  <a
                      href={u.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="break-all font-medium text-gray-800 mb-1 hover:underline"
                    >
                      {u.url}
                    </a>
                  <p className="text-xs text-gray-500 flex items-center gap-1">
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Last checked:{" "}
                    {u.last_checked_at
                      ? new Date(u.last_checked_at).toLocaleString()
                      : "Never"}
                  </p>
                </div>
                <button
                  onClick={() => handleDelete(u.id)}
                  className="text-gray-400 hover:text-red-600 transition-colors ml-4 p-2 rounded-lg hover:bg-red-50"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Summaries */}
        <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">Change Summaries</h3>

          {loading && (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          )}

          {!loading && results.length === 0 && (
            <div className="text-center py-8">
              <svg className="w-16 h-16 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="text-gray-400">No summaries available yet</p>
            </div>
          )}

          {results.map((r) => (
            <UrlCard key={r.url} {...r} />
          ))}
        </div>
      </div>
    </div>
  );
}