import sqlite3
import uuid
from pathlib import Path
from config import settings

DB = Path(settings.workdir) / "jobs.sqlite3"

def conn():
    DB.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with conn() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL,
            youtube_video_id TEXT,
            youtube_url TEXT,
            error TEXT
        )
        """)
        c.commit()

def create_job():
    job_id = uuid.uuid4().hex[:12]
    with conn() as c:
        c.execute("INSERT INTO jobs(job_id,status) VALUES (?,?)", (job_id, "created"))
        c.commit()
    return job_id

def update_job(job_id, status, youtube_video_id=None, youtube_url=None, error=None):
    with conn() as c:
        c.execute("""
        UPDATE jobs
        SET status=?, youtube_video_id=COALESCE(?, youtube_video_id),
            youtube_url=COALESCE(?, youtube_url), error=COALESCE(?, error)
        WHERE job_id=?
        """, (status, youtube_video_id, youtube_url, error, job_id))
        c.commit()

def job_exists_today():
    with conn() as c:
        row = c.execute("""
        SELECT 1 FROM jobs
        WHERE date(created_at, 'localtime') = date('now','localtime')
        AND status NOT IN ('failed')
        LIMIT 1
        """).fetchone()
        return row is not None

def get_recent_productions(limit=30):
    # The full production JSON is stored on disk; this table is intentionally lightweight.
    # Returning recent YouTube titles would require another metadata table, so we keep
    # a simple list of successful job IDs for the creative director.
    with conn() as c:
        rows = c.execute("""
        SELECT job_id, created_at, status, youtube_video_id, youtube_url
        FROM jobs ORDER BY created_at DESC LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]
