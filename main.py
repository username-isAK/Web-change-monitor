from apscheduler.schedulers.blocking import BlockingScheduler
from agents.monitor import monitor_url
from config.targets import TARGET_URLS
from utils.logger import log

scheduler = BlockingScheduler()

for url in TARGET_URLS:
    scheduler.add_job(
        monitor_url,
        trigger="interval",
        minutes=5,
        args=[url]
    )

log("Autonomous Web Change Monitoring Agent started.")
scheduler.start()
