import os
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("POLLINATIONS_API_KEY", "")
headers = {"Authorization": f"Bearer {key}"} if key else {}

r = requests.get("https://gen.pollinations.ai/v1/models", headers=headers, timeout=30)
r.raise_for_status()
data = r.json()

models = data.get("data", data if isinstance(data, list) else [])

print("\nTEXT / CHAT")
for m in models:
    mid = m.get("id", "")
    if "text" in str(m.get("capabilities", "")).lower() or "chat" in str(m.get("type", "")).lower():
        print(mid)

print("\nVIDEO")
for m in models:
    mid = m.get("id", "")
    raw = str(m).lower()
    if "video" in raw:
        print(mid)

print("\nIMAGE")
for m in models:
    mid = m.get("id", "")
    raw = str(m).lower()
    if "image" in raw:
        print(mid)

print("\nAUDIO / VOICE")
for m in models:
    mid = m.get("id", "")
    raw = str(m).lower()
    if "audio" in raw or "voice" in raw or "speech" in raw:
        print(mid)
