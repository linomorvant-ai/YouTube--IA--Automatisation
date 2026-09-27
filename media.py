from pathlib import Path
from urllib.parse import quote
import requests
from config import settings

BASE = "https://gen.pollinations.ai"

class PollinationsMediaProvider:
    def __init__(self):
        if not settings.pollinations_api_key:
            raise RuntimeError("POLLINATIONS_API_KEY is missing.")

    def _headers(self):
        return {"Authorization": f"Bearer {settings.pollinations_api_key}"}

    def generate_video(self, prompt, duration, output: Path):
        if not settings.pollinations_video_model:
            raise RuntimeError(
                "POLLINATIONS_VIDEO_MODEL is empty. Run `python discover_models.py` "
                "and choose a currently available video model."
            )

        url = f"{BASE}/video/{quote(prompt, safe='')}"
        params = {
            "model": settings.pollinations_video_model,
            "duration": max(1, min(int(duration), 10)),
        }
        r = requests.get(url, params=params, headers=self._headers(), timeout=360)
        r.raise_for_status()

        content_type = r.headers.get("content-type", "")
        if "application/json" in content_type:
            payload = r.json()
            data = payload.get("data", [{}])[0]
            if data.get("url"):
                r2 = requests.get(data["url"], timeout=360)
                r2.raise_for_status()
                output.write_bytes(r2.content)
                return
            if data.get("b64_json"):
                import base64
                output.write_bytes(base64.b64decode(data["b64_json"]))
                return
            raise RuntimeError(f"Video API returned JSON without media: {payload}")

        output.write_bytes(r.content)

    def generate_image(self, prompt, output: Path, width=1280, height=720):
        url = f"{BASE}/image/{quote(prompt, safe='')}"
        params = {
            "model": settings.pollinations_image_model,
            "width": width,
            "height": height,
        }
        r = requests.get(url, params=params, headers=self._headers(), timeout=180)
        r.raise_for_status()
        output.write_bytes(r.content)

    def generate_tts(self, text, output: Path):
        url = f"{BASE}/audio/{quote(text, safe='')}"
        params = {"voice": settings.pollinations_voice}
        r = requests.get(url, params=params, headers=self._headers(), timeout=180)
        r.raise_for_status()
        output.write_bytes(r.content)
