# main.py
import sqlite3
from datetime import datetime
from agents.fetcher import fetch_html
from agents.cleaner import clean_html
from utils.logger import log
from agents.comparator import compare_snapshots


DB_PATH = "db/web_monitor.db"

def store_snapshot(url, content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # create table if not exists
    c.execute('''
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY,
            url TEXT,
            timestamp TEXT,
            content TEXT
        )
    ''')

    # insert new snapshot
    c.execute(
        "INSERT INTO snapshots (url, timestamp, content) VALUES (?, ?, ?)",
        (url, datetime.now().isoformat(), content)
    )
    conn.commit()
    conn.close()
    log(f"Snapshot stored for {url}")

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


if __name__ == "__main__":
    url = "https://en.wikipedia.org/wiki/Artificial_intelligence"

    log(f"Fetching HTML for {url}")
    html = fetch_html(url)

    log("Cleaning HTML ...")
    clean_text = clean_html(html)

    log("Fetching previous snapshot ...")
    old_snapshot = get_last_snapshot(url)

    if old_snapshot:
        log("Comparing with previous snapshot ...")
        diff = compare_snapshots(old_snapshot, clean_text)

        if diff:
            log("⚠️ Change detected!")
            print(diff)
        else:
            log("No meaningful change detected.")
    else:
        log("No previous snapshot found (first run).")

    log("Storing new snapshot ...")
    store_snapshot(url, clean_text)

