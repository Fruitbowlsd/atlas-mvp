"""Authentifizierung und Tenant-Aufloesung.

Bewusst zwei getrennte Ebenen (Abschnitt 13.4):

  "Wer bist du"      -> get_current_user()      : Session-Cookie -> User
  "Was darfst du"    -> get_current_tenant_id() : User -> tenant_id

Die Router haengen ausschliesslich an get_current_tenant_id() und bekommen von
dort nur eine int-ID. Dadurch war der Wechsel vom gemeinsamen Passwort auf echte
Nutzerkonten auf diese Datei beschraenkt -- keine einzige Filterzeile in den
Routern musste angefasst werden.
"""
import hashlib
import hmac
import os
import secrets
from datetime import datetime

from fastapi import Cookie, Depends, Header, HTTPException, Response
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy.orm import Session

from . import models
from .database import get_db

COOKIE_NAME = "atlas_session"

SECRET = os.getenv("ATLAS_SESSION_SECRET", "atlas-dev-secret-change-me")
# Auf Railway (HTTPS) auf "true" setzen; lokal ueber HTTP muss es "false" sein,
# sonst wird der Cookie vom Browser nicht gespeichert.
COOKIE_SECURE = os.getenv("ATLAS_COOKIE_SECURE", "false").lower() == "true"

# Sitzungsdauer (Abschnitt: Session-Timeout). Nach Ablauf laeuft der naechste
# Request in ein 401 und das Frontend zeigt wieder die Login-Seite.
SESSION_MAX_AGE_SECONDS = 8 * 60 * 60

_serializer = URLSafeTimedSerializer(SECRET, salt="atlas-session")


# --- Passwoerter ------------------------------------------------------------
# PBKDF2 aus der Standardbibliothek -- ausreichend und ohne zusaetzliche
# Abhaengigkeit mit Kompilier-Aufwand (bcrypt/argon2).
_PBKDF2_ROUNDS = 240_000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _PBKDF2_ROUNDS)
    return f"pbkdf2_sha256${_PBKDF2_ROUNDS}${salt}${digest.hex()}"


def verify_password(password: str, stored: str | None) -> bool:
    if not stored:
        return False
    try:
        algorithm, rounds, salt, expected = stored.split("$")
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(rounds))
    return hmac.compare_digest(digest.hex(), expected)


# --- Session ----------------------------------------------------------------

def set_session_cookie(response: Response, user_id: int) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=_serializer.dumps({"uid": user_id}),
        httponly=True,
        samesite="lax",
        secure=COOKIE_SECURE,
        max_age=SESSION_MAX_AGE_SECONDS,
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(key=COOKIE_NAME, samesite="lax", secure=COOKIE_SECURE)


def _user_id_from_cookie(raw: str | None) -> int | None:
    if not raw:
        return None
    try:
        data = _serializer.loads(raw, max_age=SESSION_MAX_AGE_SECONDS)
    except SignatureExpired:
        return None   # Sitzung abgelaufen -> wie nicht angemeldet
    except BadSignature:
        return None
    return data.get("uid")


def get_optional_user(
    db: Session = Depends(get_db),
    atlas_session: str | None = Cookie(default=None),
) -> models.User | None:
    user_id = _user_id_from_cookie(atlas_session)
    if user_id is None:
        return None
    user = db.query(models.User).filter(models.User.id == user_id).first()
    # Deaktivierte Nutzer verlieren den Zugang sofort, auch mit gueltigem Cookie.
    if not user or not user.is_active:
        return None
    return user


def get_current_user(user: models.User | None = Depends(get_optional_user)) -> models.User:
    if user is None:
        raise HTTPException(status_code=401, detail="Nicht angemeldet")
    return user


def require_auth(user: models.User = Depends(get_current_user)) -> None:
    """Beibehaltener Name, damit die bestehenden Router unveraendert bleiben."""
    return None


# --- "Was darfst du sehen": Tenant-Aufloesung -------------------------------

def get_current_tenant_id(user: models.User = Depends(get_current_user)) -> int:
    """Tenant, dessen Kundendaten der Aufrufer sehen darf.

    Frueher lieferte diese Funktion fest den einzigen Demo-Tenant; jetzt kommt sie
    aus dem angemeldeten Nutzer. Die Filterzeilen in den Routern blieben davon
    unberuehrt -- genau dafuer war die Trennung gedacht.
    """
    return user.tenant_id


def require_internal(
    user: models.User = Depends(get_current_user),
    x_atlas_internal: str | None = Header(default=None),
) -> None:
    """Zugang zum internen Kurations-Bereich (Abschnitt 13.2, Punkt 4). Geteiltes
    Atlas-Wissen, kein Kundengeheimnis -- daher keine Tenant-Filterung, sondern
    eine eigene Stufe neben dem Nutzer-Login.

    Ist ATLAS_INTERNAL_TOKEN nicht gesetzt, genuegt ein normaler Login wie bisher.
    """
    expected = os.getenv("ATLAS_INTERNAL_TOKEN")
    if not expected:
        return
    if not x_atlas_internal or not hmac.compare_digest(x_atlas_internal, expected):
        raise HTTPException(status_code=403, detail="Kein Zugriff auf den internen Bereich")


# --- Login-Hilfen -----------------------------------------------------------

def find_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email.strip().lower()).first()


def tenant_for_email(db: Session, email: str) -> models.Tenant | None:
    """Tenant anhand der Mail-Domain. Grundlage sowohl fuer die Frage, ob im zweiten
    Login-Schritt SSO oder Passwort angeboten wird, als auch fuer die Zuordnung
    neuer SSO-Nutzer."""
    _, _, domain = email.strip().lower().partition("@")
    if not domain:
        return None
    return db.query(models.Tenant).filter(models.Tenant.email_domain == domain).first()


def mark_logged_in(db: Session, user: models.User) -> None:
    user.last_login_at = datetime.utcnow()
    db.commit()
