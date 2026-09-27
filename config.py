import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    workdir: str = os.getenv("WORKDIR", "work")
    daily_upload_time: str = os.getenv("DAILY_UPLOAD_TIME", "15:00")
    timezone: str = os.getenv("TIMEZONE", "Europe/Paris")
    videos_per_day: int = int(os.getenv("VIDEOS_PER_DAY", "1"))
    allow_multiple_runs: bool = os.getenv("ALLOW_MULTIPLE_RUNS", "false").lower() == "true"

    test_mode: bool = os.getenv("TEST_MODE", "true").lower() == "true"
    youtube_visibility: str = os.getenv("YOUTUBE_VISIBILITY", "private")

    language: str = os.getenv("LANGUAGE", "fr")
    target_age: str = os.getenv("TARGET_AGE", "4-8")
    video_duration_min: int = int(os.getenv("VIDEO_DURATION_MIN", "180"))
    video_duration_max: int = int(os.getenv("VIDEO_DURATION_MAX", "300"))
    scene_count: int = int(os.getenv("SCENE_COUNT", "6"))

    llm_provider: str = os.getenv("LLM_PROVIDER", "pollinations")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

    pollinations_api_key: str = os.getenv("POLLINATIONS_API_KEY", "")
    pollinations_text_model: str = os.getenv("POLLINATIONS_TEXT_MODEL", "openai/gpt-5.4-nano")
    pollinations_video_model: str = os.getenv("POLLINATIONS_VIDEO_MODEL", "")
    pollinations_image_model: str = os.getenv("POLLINATIONS_IMAGE_MODEL", "flux")
    pollinations_voice: str = os.getenv("POLLINATIONS_VOICE", "nova")

    youtube_client_id: str = os.getenv("YOUTUBE_CLIENT_ID", "")
    youtube_client_secret: str = os.getenv("YOUTUBE_CLIENT_SECRET", "")
    youtube_refresh_token: str = os.getenv("YOUTUBE_REFRESH_TOKEN", "")
    youtube_category_id: str = os.getenv("YOUTUBE_CATEGORY_ID", "24")

    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")

    log_level: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
