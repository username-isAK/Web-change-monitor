# 🤖Autonomous Web Change Monitoring Agent

An AI-powered tool that monitors web pages for changes, summarizes differences and highlights their importance. The project uses **Python**, **Playwright**, and **FastAPI** to enable both local execution and API-driven interaction.

---

## ⚡Features

- Monitor multiple web pages for content changes
- Detect changes at granular levels using **DeepDiff**
- Generate **summaries of detected changes** for quick understanding
- Scheduled checks with **APScheduler**
- Store historical page snapshots in **SQLite**
- **REST API using FastAPI** to manage monitored pages and retrieve results
- Fully functional locally without requiring an external server

---

## ⚙️Tech Stack

| Tool | Purpose |
|------|---------|
| **Python** | Core logic and scheduling |
| **Playwright** | Automated web page fetching |
| **BeautifulSoup** | HTML parsing and content extraction |
| **DeepDiff** | Precise comparison of old and new page content |
| **SQLite** | Local storage for snapshots |
| **APScheduler** | Scheduling periodic web checks |
| **FastAPI** | REST API for managing monitored pages and accessing results |
