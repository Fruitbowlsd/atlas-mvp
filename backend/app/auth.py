import hashlib
import hmac
import os

from fastapi import Cookie, HTTPException, Response

COOKIE_NAME = "atlas_auth"

# Passwort und Secret kommen aus Umgebungsvariablen (z.B. Railway-Variablen).
# Fallback-Werte nur fuer lokale Entwicklung -- fuer den echten Demo-Einsatz
# unbedingt ATLAS_DEMO_PASSWORD in der Deploy-Umgebung setzen.
DEMO_PASSWORD = os.getenv("ATLAS_DEMO_PASSWORD", "atlas-demo")
SECRET = os.getenv("ATLAS_SESSION_SECRET", "atlas-dev-secret-change-me")
# Auf Railway (HTTPS) auf "true" setzen; lokal ueber HTTP muss es "false" sein,
# sonst wird der Cookie vom Browser nicht gespeichert.
COOKIE_SECURE = os.getenv("ATLAS_COOKIE_SECURE", "false").lower() == "true"


def _token_for(password: str) -> str:
    return hmac.new(SECRET.encode(), password.encode(), hashlib.sha256).hexdigest()


VALID_TOKEN = _token_for(DEMO_PASSWORD)


def check_password(password: str) -> bool:
    return hmac.compare_digest(password, DEMO_PASSWORD)


def set_auth_cookie(response: Response) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=VALID_TOKEN,
        httponly=True,
        samesite="lax",
        secure=COOKIE_SECURE,
        max_age=60 * 60 * 12,  # 12 Stunden
    )


def is_authenticated(atlas_auth: str | None = Cookie(default=None)) -> bool:
    return atlas_auth is not None and hmac.compare_digest(atlas_auth, VALID_TOKEN)


def require_auth(atlas_auth: str | None = Cookie(default=None)) -> None:
    if not is_authenticated(atlas_auth):
        raise HTTPException(status_code=401, detail="Nicht angemeldet")
