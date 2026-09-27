# YouTube AI Automation

Automate a daily children-oriented YouTube video:

Scheduler → LLM creative director → structured JSON → video scenes → TTS → subtitles → FFmpeg → thumbnail → YouTube upload.

## Important reality check

The orchestration code can run on GitHub Actions. Standard Actions usage is free for public repositories, while private repositories have plan quotas. However, AI generation is not automatically free. Pollinations currently uses a Pollen credit system; free/quest credits are not a guaranteed unlimited monthly allowance. OpenAI API usage is paid according to current API pricing.

The project therefore separates providers and keeps all API keys in GitHub Secrets.

## 1. Local test

Install Python 3.12 and FFmpeg.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Windows PowerShell activation:

```powershell
.venv\Scripts\Activate.ps1
```

Fill `.env`.

## 2. Discover current Pollinations models

Model IDs can change. Run:

```bash
python discover_models.py
```

Choose a currently available video model and set:

```text
POLLINATIONS_VIDEO_MODEL=...
```

Do not assume an old model name remains available.

## 3. YouTube OAuth

YouTube uploads require OAuth 2.0. A service account is not supported for normal YouTube channel access.

Create a Google Cloud project, enable YouTube Data API v3, and create OAuth credentials.

You need a long-lived refresh token with the scope:

```text
https://www.googleapis.com/auth/youtube.upload
```

Store these as secrets:

```text
YOUTUBE_CLIENT_ID
YOUTUBE_CLIENT_SECRET
YOUTUBE_REFRESH_TOKEN
```

Google's OAuth documentation explains offline access and refresh tokens.

## 4. Test mode

Keep:

```text
TEST_MODE=true
YOUTUBE_VISIBILITY=private
```

The first run uploads the result privately.

Only after checking the video should you switch to:

```text
TEST_MODE=false
YOUTUBE_VISIBILITY=public
```

## 5. GitHub Actions

Create a public GitHub repository and upload this project.

Repository → Settings → Secrets and variables → Actions.

Secrets:

```text
POLLINATIONS_API_KEY
YOUTUBE_CLIENT_ID
YOUTUBE_CLIENT_SECRET
YOUTUBE_REFRESH_TOKEN
```

Optional:

```text
OPENAI_API_KEY
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

Variables:

```text
POLLINATIONS_TEXT_MODEL
POLLINATIONS_VIDEO_MODEL
OPENAI_MODEL
TEST_MODE
YOUTUBE_VISIBILITY
```

Run the workflow manually first.

## 6. Scheduling

The included workflow is configured for 13:00 UTC, corresponding to 15:00 in France during summer time. For exact year-round Europe/Paris scheduling, use an external scheduler or change the cron twice yearly. GitHub Actions cron is UTC.

## 7. Architecture

```text
GitHub Actions
      ↓
Python orchestrator
      ↓
LLM
      ↓
Structured production JSON
      ↓
┌──────────────┬───────────────┐
↓              ↓               ↓
Video API      TTS API         Image API
↓              ↓               ↓
Scenes         Voice           Thumbnail
└──────────────┼───────────────┘
               ↓
             FFmpeg
               ↓
          final.mp4
               ↓
         quality checks
               ↓
         YouTube Data API
               ↓
            upload
               ↓
          thumbnail
               ↓
           publish
```

## 8. Current limitations

1. Free AI generation is not guaranteed at one 3–5 minute video every day.
2. Video generation is the largest likely cost/bottleneck.
3. GitHub Actions is an orchestrator/runner, not a GPU video-generation service.
4. YouTube API uploads from unverified projects can be restricted to private viewing until the project passes Google's required audit.
5. Children's content must comply with YouTube's current audience, privacy, safety, and monetization rules.
6. The code deliberately defaults to private uploads.

## 9. Production hardening

Before running unattended:

- add a persistent external database/object storage if you need long-term archives;
- add a second media provider as fallback;
- add content moderation;
- add a budget guard before each paid API call;
- use a dedicated YouTube OAuth client;
- monitor API failures and quota consumption;
- keep test mode enabled until several runs succeed.
