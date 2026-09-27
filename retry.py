import time
import logging
from config import settings

log = logging.getLogger("youtube-ai")

def with_retries(fn, name, attempts=3, base_delay=5):
    last = None
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except Exception as exc:
            last = exc
            log.warning("%s failed attempt %s/%s: %s", name, attempt, attempts, exc)
            if attempt < attempts:
                time.sleep(base_delay * attempt)
    raise RuntimeError(f"{name} failed after {attempts} attempts") from last
