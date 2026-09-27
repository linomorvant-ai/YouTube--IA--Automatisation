import subprocess
from pathlib import Path
from datetime import timedelta

def _run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr[-4000:])
    return result

def create_srt(scenes, output: Path):
    cursor = 0
    lines = []
    for i, scene in enumerate(scenes, start=1):
        duration = int(scene["duration_seconds"])
        start = format_srt_time(cursor)
        end = format_srt_time(cursor + duration)
        text = scene["narration"].replace("\n", " ").strip()
        lines += [str(i), f"{start} --> {end}", text, ""]
        cursor += duration
    output.write_text("\n".join(lines), encoding="utf-8")

def format_srt_time(seconds):
    ms = int((seconds - int(seconds)) * 1000)
    whole = int(seconds)
    h = whole // 3600
    m = (whole % 3600) // 60
    s = whole % 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def render_video(scene_files, voice_files, output: Path, subtitles: Path):
    work = output.parent / "ffmpeg_work"
    work.mkdir(parents=True, exist_ok=True)

    # Normalize every scene to 1080p H.264/AAC.
    normalized = []
    for i, (scene, voice) in enumerate(zip(scene_files, voice_files), start=1):
        out = work / f"n_{i:02d}.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-i", str(scene),
            "-i", str(voice),
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,"
                   "pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
            "-r", "30",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            "-shortest",
            str(out),
        ]
        _run(cmd)
        normalized.append(out)

    concat = work / "concat.txt"
    concat.write_text(
        "".join(f"file '{p.resolve().as_posix()}'\n" for p in normalized),
        encoding="utf-8",
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat),
        "-vf", f"subtitles={subtitles.resolve().as_posix()}",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        str(output),
    ]
    _run(cmd)
