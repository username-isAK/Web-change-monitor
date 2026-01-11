from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from Backend.agents.monitor import monitor_url
from Backend.config.targets import TARGET_URLS
from Backend.utils.logger import log
from Backend.db.repository import get_last_snapshot, get_last_analysis

app = FastAPI()
scheduler = BackgroundScheduler()

@app.on_event("startup")
def start_scheduler():
    for url in TARGET_URLS:
        scheduler.add_job(
            monitor_url,
            trigger="interval",
            minutes=5,
            args=[url],
            id=url
        )
    scheduler.start()
    log("Autonomous Web Change Monitoring Agent started.")

# Example API endpoint to fetch last snapshot for a URL
@app.get("/snapshot")
def get_snapshot(url: str):
    content = get_last_snapshot(url)
    return {"url": url, "snapshot": content}


@app.get("/summary")
def get_summary(url: str):
    analysis = get_last_analysis(url)
    if analysis:
        return {"url": url, "analysis": analysis}
    return {"url": url, "analysis": None, "message": "No analysis available yet"}

