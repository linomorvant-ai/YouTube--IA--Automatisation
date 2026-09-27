import os
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

from config import settings
from db import init_db, job_exists_today, create_job, update_job
from retry import with_retries
from llm import CreativeDirector
from media import PollinationsMediaProvider
from editor import render_video, create_srt
from youtube import YouTubeUploader
from validation import validate_production
from notifier import notify

load_dotenv()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger("youtube-ai")

BASE = Path(settings.workdir)
BASE.mkdir(parents=True, exist_ok=True)

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def run():
    init_db()
    if job_exists_today() and not settings.allow_multiple_runs:
        log.info("A job already exists for today. Exiting.")
        return

    job_id = create_job()
    log.info("JOB START %s", job_id)

    job_dir = BASE / job_id
    for d in ["scenes", "audio", "sfx", "music", "output", "thumbnail", "subtitles"]:
        (job_dir / d).mkdir(parents=True, exist_ok=True)

    try:
        director = CreativeDirector()
        media = PollinationsMediaProvider()
        update_job(job_id, "creative")

        history = director.load_history()
        production = with_retries(
            lambda: director.create_production(history),
            "creative_generation",
        )
        (job_dir / "production.json").write_text(
            json.dumps(production, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        validate_production(production)
        log.info("SCENE PLAN VALIDATED")

        update_job(job_id, "generating_media")

        scene_files = []
        voice_files = []

        for scene in production["scenes"]:
            sid = int(scene["id"])
            video_path = job_dir / "scenes" / f"scene_{sid:02d}.mp4"
            voice_path = job_dir / "audio" / f"scene_{sid:02d}.mp3"

            if not video_path.exists():
                log.info("Generating scene %s", sid)
                with_retries(
                    lambda s=scene: media.generate_video(
                        prompt=s["visual_prompt"],
                        duration=s["duration_seconds"],
                        output=video_path,
                    ),
                    f"video_scene_{sid}",
                )
            scene_files.append(video_path)

            if not voice_path.exists():
                log.info("Generating voice %s", sid)
                with_retries(
                    lambda s=scene: media.generate_tts(
                        text=s["narration"],
                        output=voice_path,
                    ),
                    f"tts_scene_{sid}",
                )
            voice_files.append(voice_path)

        srt_path = job_dir / "subtitles" / "subtitles.srt"
        create_srt(production["scenes"], srt_path)

        thumbnail_path = job_dir / "thumbnail" / "thumbnail.jpg"
        if not thumbnail_path.exists():
            with_retries(
                lambda: media.generate_image(
                    prompt=production["thumbnail_prompt"],
                    output=thumbnail_path,
                    width=1280,
                    height=720,
                ),
                "thumbnail",
            )

        update_job(job_id, "editing")
        final_video = job_dir / "output" / "final.mp4"

        if not final_video.exists():
            with_retries(
                lambda: render_video(
                    scene_files=scene_files,
                    voice_files=voice_files,
                    output=final_video,
                    subtitles=srt_path,
                ),
                "ffmpeg_render",
            )

        validate_production(production)
        validate_media(final_video, thumbnail_path)

        update_job(job_id, "ready_for_youtube")

        if settings.test_mode:
            log.info("TEST_MODE=true: YouTube upload will be private.")
            visibility = "private"
        else:
            visibility = settings.youtube_visibility

        uploader = YouTubeUploader()
        result = with_retries(
            lambda: uploader.upload(
                video_path=final_video,
                title=production["youtube"]["title"],
                description=production["youtube"]["description"],
                tags=production["youtube"]["tags"],
                thumbnail_path=thumbnail_path,
                privacy_status=visibility,
                made_for_kids=True,
                publish_at=None,
            ),
            "youtube_upload",
        )

        update_job(
            job_id,
            "published" if visibility != "private" else "uploaded_private",
            youtube_video_id=result["video_id"],
            youtube_url=result["url"],
        )

        notify(
            f"✓ Vidéo terminée\n"
            f"Titre : {production['youtube']['title']}\n"
            f"Statut : {visibility}\n"
            f"URL : {result['url']}"
        )
        log.info("JOB COMPLETE %s", job_id)

    except Exception as exc:
        log.exception("JOB FAILED %s", job_id)
        update_job(job_id, "failed", error=str(exc))
        notify(f"❌ Échec du job {job_id}\nÉtape : voir les logs\nErreur : {exc}")
        raise

def validate_media(video_path: Path, thumbnail_path: Path):
    if not video_path.exists() or video_path.stat().st_size < 10_000:
        raise RuntimeError("Final video is missing or suspiciously small.")
    if not thumbnail_path.exists() or thumbnail_path.stat().st_size < 1_000:
        raise RuntimeError("Thumbnail is missing or suspiciously small.")

if __name__ == "__main__":
    run()
