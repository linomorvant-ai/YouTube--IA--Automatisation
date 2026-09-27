import requests
from config import settings

def notify(message):
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    try:
        requests.post(
            url,
            json={"chat_id": settings.telegram_chat_id, "text": message},
            timeout=20,
        ).raise_for_status()
    except Exception:
        # Notification failure must never break the production job.
        pass
