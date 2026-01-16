from Backend.agents.fetcher import fetch_html
from Backend.agents.cleaner import clean_html
from Backend.agents.comparator import compare_snapshots
from Backend.utils.logger import log
from Backend.db.repository import (
    get_last_snapshot,
    store_snapshot,
    store_ai_analysis,
    create_notification
)
from Backend.agents.extractor import extract_changes
from Backend.agents.llm_analyzer import analyze_changes

def monitor_url(user_id: int, url_id: int, url: str):
    log(f"Monitoring {url} for user {user_id}")

    try:
        html = fetch_html(url)
    except Exception as e:
        log(f"Failed to fetch {url}: {e}")
        return

    clean_text = clean_html(html)
    old_snapshot = get_last_snapshot(user_id, url)

    if old_snapshot:
        diff = compare_snapshots(old_snapshot, clean_text)

        if diff:
            changes = extract_changes(diff)

            if changes:
                try:
                    analysis = analyze_changes(changes, url)

                    store_ai_analysis(user_id, url, analysis)
                    summary = analysis.get("summary")
                    message = (
                        summary[0]
                        if isinstance(summary, list) and summary
                        else "Website content changed"
                    )

                    create_notification(
                        user_id=user_id,
                        url=url,
                        message=message,
                        importance=analysis.get("importance", "medium")
                    )

                    log("🔔 Notification created")

                except Exception as e:
                    log(f"LLM analysis failed: {e}")
        else:
            log("No meaningful change detected.")
    else:
        log("First run — creating baseline snapshot.")

    store_snapshot(user_id, url, clean_text)

