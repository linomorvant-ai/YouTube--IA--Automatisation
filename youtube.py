from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config import settings

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

class YouTubeUploader:
    def __init__(self):
        required = [
            settings.youtube_client_id,
            settings.youtube_client_secret,
            settings.youtube_refresh_token,
        ]
        if not all(required):
            raise RuntimeError(
                "YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET and "
                "YOUTUBE_REFRESH_TOKEN are required."
            )

        creds = Credentials(
            token=None,
            refresh_token=settings.youtube_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.youtube_client_id,
            client_secret=settings.youtube_client_secret,
            scopes=SCOPES,
        )
        self.youtube = build("youtube", "v3", credentials=creds)

    def upload(
        self,
        video_path: Path,
        title: str,
        description: str,
        tags,
        thumbnail_path: Path,
        privacy_status="private",
        made_for_kids=True,
        publish_at=None,
    ):
        body = {
            "snippet": {
                "title": title[:100],
                "description": description,
                "tags": tags[:30] if isinstance(tags, list) else [],
                "categoryId": settings.youtube_category_id,
                "defaultLanguage": settings.language,
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": bool(made_for_kids),
            },
        }

        if publish_at:
            body["status"]["publishAt"] = publish_at
            body["status"]["privacyStatus"] = "private"

        request = self.youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=MediaFileUpload(
                str(video_path),
                mimetype="video/mp4",
                resumable=True,
            ),
        )

        response = None
        while response is None:
            _, response = request.next_chunk()

        video_id = response["id"]

        self.youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(
                str(thumbnail_path),
                mimetype="image/jpeg",
            ),
        ).execute()

        return {
            "video_id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}",
        }
