from agents.fetcher import fetch_html
from agents.cleaner import clean_html
from agents.comparator import compare_snapshots
from utils.logger import log
from db.repository import get_last_snapshot, store_snapshot

def monitor_url(url):
    log(f"Monitoring {url}")

    html = fetch_html(url)
    clean_text = clean_html(html)

    old_snapshot = get_last_snapshot(url)

    if old_snapshot:
        diff = compare_snapshots(old_snapshot, clean_text)
        if diff:
            log("⚠️ Change detected!")
            print(diff)
        else:
            log("No meaningful change detected.")
    else:
        log("First run — creating baseline snapshot.")

    store_snapshot(url, clean_text)
