from apscheduler.schedulers.background import BackgroundScheduler
from Backend.agents.monitor import monitor_url
from Backend.utils.logger import log

scheduler = BackgroundScheduler()

def start_scheduler():
    if scheduler.running:
        return
    scheduler.start()
    log("Scheduler started")

def _job_id(user_id: int, url_id: int) -> str:
    return f"user-{user_id}-url-{url_id}"

def add_url_job(user_id: int, url_id: int, url: str):
    job_id = f"user-{user_id}-url-{url_id}"

    scheduler.add_job(
        monitor_url,
        trigger="interval",
        minutes=10,
        args=[user_id, url_id, url],
        id=job_id,
        replace_existing=True
    )

    log(f"Scheduled monitoring for {url} (job={job_id})")

def remove_url_job(user_id: int, url_id: int):
    job_id = _job_id(user_id, url_id)

    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        log(f"Stopped monitoring job {job_id}")
