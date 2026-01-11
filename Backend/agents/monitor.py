from Backend.agents.fetcher import fetch_html
from Backend.agents.cleaner import clean_html
from Backend.agents.comparator import compare_snapshots
from Backend.utils.logger import log
from Backend.db.repository import get_last_snapshot, store_snapshot, store_ai_analysis
from Backend.agents.extractor import extract_changes
from Backend.agents.llm_analyzer import analyze_changes

def monitor_url(url):
    log(f"Monitoring {url}")

    try:
        html = fetch_html(url)
    except Exception as e:
        log(f"Failed to fetch {url}: {e}")
        return

    clean_text = clean_html(html)
    old_snapshot = get_last_snapshot(url)

    if old_snapshot:
        diff = compare_snapshots(old_snapshot, clean_text)
        if diff:
            changes = extract_changes(diff)
            if changes:
                try:
                    analysis = analyze_changes(changes, url)
                    store_ai_analysis(url, analysis)
                    log("🔍 AI Analysis:")
                    print(analysis)

                except Exception as e:
                    log(f"LLM analysis failed: {e}")
        else:
            log("No meaningful change detected.")
    else:
        log("First run — creating baseline snapshot.")

    store_snapshot(url, clean_text)

