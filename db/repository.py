import sqlite3
from datetime import datetime
import json
DB_PATH = "db/web_monitor.db"

def store_snapshot(url, content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY,
            url TEXT,
            timestamp TEXT,
            content TEXT
        )
    """)

    c.execute(
        "INSERT INTO snapshots (url, timestamp, content) VALUES (?, ?, ?)",
        (url, datetime.now().isoformat(), content)
    )

    conn.commit()
    conn.close()

def get_last_snapshot(url):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        "SELECT content FROM snapshots WHERE url = ? ORDER BY id DESC LIMIT 1",
        (url,)
    )

    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def store_ai_analysis(url, analysis):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS ai_analysis (
            id INTEGER PRIMARY KEY,
            url TEXT,
            timestamp TEXT,
            summary TEXT,
            importance TEXT,
            reasoning TEXT
        )
    """)

    c.execute(
        """
        INSERT INTO ai_analysis (url, timestamp, summary, importance, reasoning)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            url,
            datetime.now().isoformat(),
            json.dumps(analysis.get("summary")),
            analysis.get("importance"),
            analysis.get("reasoning"),
        )
    )

    conn.commit()
    conn.close()