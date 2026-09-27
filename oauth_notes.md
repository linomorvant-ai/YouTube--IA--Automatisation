# YouTube OAuth notes

The automation needs offline OAuth access so it can refresh access tokens while you are not present.

Required scope:

https://www.googleapis.com/auth/youtube.upload

Google does not support using a service account as a substitute for authenticating a normal YouTube channel.

The long-lived value stored in GitHub is the refresh token. Treat it like a password.

Recommended sequence:

1. Create Google Cloud project.
2. Enable YouTube Data API v3.
3. Configure OAuth consent screen.
4. Create OAuth client credentials.
5. Authorize the YouTube account with the upload scope and offline access.
6. Store the refresh token as a GitHub Actions secret.
7. Never commit the client secret or refresh token.

See Google's official OAuth 2.0 and YouTube Data API documentation.
