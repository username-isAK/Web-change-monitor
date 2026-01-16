from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from concurrent.futures import ThreadPoolExecutor
from Backend.db.repository import (
    init_users_table,
    init_urls_table,
    get_or_create_user,
    add_url,
    get_last_analysis,
    get_all_active_urls,
    init_snapshots_table,
    init_ai_analysis_table,
    get_latest_summaries_for_user,
    get_active_urls_for_user,
    delete_url, init_notifications_table, get_notifications_for_user, mark_notification_read
)
from Backend.scheduler import start_scheduler, add_url_job, remove_url_job

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UrlCreate(BaseModel):
    url: str


@app.on_event("startup")
async def startup_event():
    print("=" * 50)
    print("SERVER STARTING UP")
    print("=" * 50)
    init_users_table()
    init_urls_table()
    init_snapshots_table()
    init_ai_analysis_table()
    start_scheduler()
    urls = get_all_active_urls()
    init_notifications_table()

    for item in urls:
        add_url_job(item["user_id"], item["id"], item["url"])
    print("Startup complete!")


@app.post("/urls")
async def register_url(
        payload: UrlCreate,
        user_email: str = Header(..., alias="user-email")
    ):
    print(f"\n>>> POST /urls called")
    print(f">>> User: {user_email}")
    print(f">>> URL: {payload.url}")

    try:
        user_id = get_or_create_user(user_email)
        url_id = add_url(user_id, payload.url)
        add_url_job(user_id, url_id, payload.url)

        print(f">>> Success! URL ID: {url_id}")
        return {"message": "URL registered", "url_id": url_id}
    except Exception as e:
        print(f">>> ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/urls")
async def list_urls(user_email: str = Header(..., alias="user-email")):
    print(f"\n>>> GET /urls called for user: {user_email}")
    try:
        user_id = get_or_create_user(user_email)
        urls = get_active_urls_for_user(user_id)
        print(f">>> Found {len(urls)} URLs")
        return urls
    except Exception as e:
        print(f">>> ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/urls/{url_id}")
async def remove_url(url_id: int, user_email: str = Header(..., alias="user-email")):
    user_id = get_or_create_user(user_email)
    delete_url(user_id, url_id)
    remove_url_job(user_id, url_id)

    return {"message": "URL and all related data deleted, monitoring stopped"}


executor = ThreadPoolExecutor(max_workers=5)


@app.get("/summaries")
async def get_summaries(user_email: str = Header(..., alias="user-email")):
    user_id = get_or_create_user(user_email)
    return get_latest_summaries_for_user(user_id)


@app.get("/summary")
async def get_summary(url: str):
    print(f"\n>>> GET /summary called for: {url}")
    try:
        analysis = get_last_analysis(url)
        if analysis:
            return {"url": url, "analysis": analysis}
        return {"url": url, "message": "No analysis available yet"}
    except Exception as e:
        print(f">>> ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notifications")
async def get_notifications(
    user_email: str = Header(..., alias="user-email")
):
    user_id = get_or_create_user(user_email)
    return get_notifications_for_user(user_id)

@app.post("/notifications/{notification_id}/read")
async def mark_notification(
    notification_id: int,
    user_email: str = Header(..., alias="user-email")
):
    user_id = get_or_create_user(user_email)
    mark_notification_read(user_id, notification_id)
    return {"message": "Notification marked as read"}



if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )