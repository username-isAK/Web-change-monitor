from pathlib import Path
from datetime import datetime
import sqlite3
import json

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "web_monitor.db"

def init_users_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE
        )
    """)

    conn.commit()
    conn.close()

def init_urls_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS monitored_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            url TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT,
            last_checked_at TEXT,
            UNIQUE(user_id, url),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

def update_last_checked(user_id: int, url: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        UPDATE monitored_urls
        SET last_checked_at = ?
        WHERE user_id = ? AND url = ?
    """, (
        datetime.now().isoformat(),
        user_id,
        url
    ))

    conn.commit()
    conn.close()

def get_or_create_user(email: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT id FROM users WHERE email = ?", (email,))
    row = c.fetchone()

    if row:
        user_id = row[0]
    else:
        c.execute("INSERT INTO users (email) VALUES (?)", (email,))
        user_id = c.lastrowid

    conn.commit()
    conn.close()
    return user_id



def add_url(user_id: int, url: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        INSERT OR IGNORE INTO monitored_urls (user_id, url, active, created_at)
        VALUES (?, ?, 1, ?)
    """, (user_id, url, datetime.now().isoformat()))

    conn.commit()

    c.execute("""
        SELECT id FROM monitored_urls
        WHERE user_id = ? AND url = ?
    """, (user_id, url))

    row = c.fetchone()
    conn.close()

    return row[0]


def get_all_active_urls():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT id, user_id, url
        FROM monitored_urls
        WHERE active = 1
    """)

    rows = [
        {"id": r[0], "user_id": r[1], "url": r[2]}
        for r in c.fetchall()
    ]

    conn.close()
    return rows

def get_active_urls_for_user(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT id, url, last_checked_at
        FROM monitored_urls
        WHERE user_id = ? AND active = 1
    """, (user_id,))

    rows = [{"id": r[0], "url": r[1], "last_checked_at": r[2]} for r in c.fetchall()]

    conn.close()
    return rows



def delete_url(user_id: int, url_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Delete snapshots for this URL
    c.execute("""
        DELETE FROM snapshots
        WHERE url IN (
            SELECT url FROM monitored_urls
            WHERE id = ? AND user_id = ?
        )
    """, (url_id, user_id))

    # Delete AI analysis for this URL
    c.execute("""
        DELETE FROM ai_analysis
        WHERE url IN (
            SELECT url FROM monitored_urls
            WHERE id = ? AND user_id = ?
        )
    """, (url_id, user_id))

    # Delete the URL itself
    c.execute("""
        DELETE FROM monitored_urls
        WHERE id = ? AND user_id = ?
    """, (url_id, user_id))

    conn.commit()
    conn.close()


def init_snapshots_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS snapshots(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            url TEXT,
            timestamp TEXT,
            content TEXT
        )
    """)

    conn.commit()
    conn.close()

def init_ai_analysis_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS ai_analysis(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            url TEXT,
            timestamp TEXT,
            summary TEXT,
            importance TEXT,
            reasoning TEXT
        )
    """)

    conn.commit()
    conn.close()

def store_snapshot(user_id: int, url: str, content: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        """
        INSERT INTO snapshots (user_id, url, timestamp, content)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, url, datetime.now().isoformat(), content)
    )

    conn.commit()
    conn.close()

def get_last_snapshot(user_id: int, url: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        """
        SELECT content
        FROM snapshots
        WHERE user_id = ? AND url = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id, url)
    )

    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def store_ai_analysis(user_id: int, url: str, analysis: dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    summary_json = json.dumps(analysis.get("summary", []))
    importance = analysis.get("importance", "UNKNOWN")
    reasoning = analysis.get("reasoning", "")

    c.execute(
        """
        INSERT INTO ai_analysis
        (user_id, url, timestamp, summary, importance, reasoning)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id, url, datetime.now().isoformat(),
         summary_json, importance, reasoning)
    )

    conn.commit()
    conn.close()


def get_last_analysis(user_id: int, url: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT summary, importance, reasoning FROM ai_analysis WHERE user_id = ? AND url = ? ORDER BY id DESC LIMIT 1",
        (user_id,url)
    )
    row = c.fetchone()
    conn.close()
    if row:
        summary, importance, reasoning = row
        return {
            "summary": json.loads(summary),
            "importance": importance,
            "reasoning": reasoning
        }
    return None

def get_latest_summaries_for_user(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Get latest analysis per URL for this user
    c.execute("""
        SELECT a.url, a.summary, a.importance, a.reasoning
        FROM ai_analysis a
        JOIN (
            SELECT url, MAX(id) AS max_id
            FROM ai_analysis
            WHERE user_id = ?
            GROUP BY url
        ) latest
        ON a.url = latest.url AND a.id = latest.max_id
        WHERE a.user_id = ?
    """, (user_id, user_id))

    rows = c.fetchall()
    conn.close()

    results = []
    for url, summary, importance, reasoning in rows:
        results.append({
            "url": url,
            "summary": json.loads(summary),
            "importance": importance,
            "reasoning": reasoning
        })

    return results

def init_notifications_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            url TEXT,
            message TEXT,
            importance TEXT,
            created_at TEXT,
            read INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()

def create_notification(user_id: int, url: str, message: str, importance: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        INSERT INTO notifications (user_id, url, message, importance, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        url,
        message,
        importance,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

def get_notifications_for_user(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT id, url, message, importance, created_at, read
        FROM notifications
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))

    rows = c.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "url": r[1],
            "message": r[2],
            "importance": r[3],
            "created_at": r[4],
            "read": bool(r[5])
        }
        for r in rows
    ]

def delete_notification(user_id: int, notification_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        DELETE FROM notifications
        WHERE id = ? AND user_id = ?
    """, (notification_id, user_id))

    conn.commit()
    conn.close()



