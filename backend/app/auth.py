import hashlib
import hmac
import os

from fastapi import Cookie, Depends, Header, HTTPException, Response
from sqlalchemy.orm import Session

from . import models
from .database import get_db

COOKIE_NAME = "atlas_auth"

# Slug des Tenants, dem die Demo-Daten gehoeren. Solange es genau ein Passwort gibt,
# gibt es genau einen Tenant (Abschnitt 13.2, Punkt 3).
DEFAULT_TENANT_SLUG = "demo-gaslieferant"

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


# --- "Was darfst du sehen": Tenant-Aufloesung -------------------------------
# Bewusst getrennt von der Frage "wer bist du" (oben). Die Router bekommen aus
# get_current_tenant_id() ausschliesslich eine int-ID -- nie Cookie, Passwort oder
# Nutzer. Dadurch ist der spaetere SSO-Umbau auf genau diese eine Funktion begrenzt:
# statt des Default-Tenants liefert sie dann den Tenant des angemeldeten Nutzers,
# die Filterzeilen in den Routern bleiben unveraendert (Abschnitt 13.4).

def get_current_tenant_id(
    db: Session = Depends(get_db),
    atlas_auth: str | None = Cookie(default=None),
) -> int:
    """Tenant, dessen Kundendaten der Aufrufer sehen darf.

    Heute: ein gemeinsames Passwort = genau ein Tenant. Beim Umstieg auf echte
    Nutzerkonten wird NUR der Rumpf dieser Funktion ersetzt (Session -> User ->
    user.tenant_id).
    """
    require_auth(atlas_auth)

    tenant = db.query(models.Tenant).filter(models.Tenant.slug == DEFAULT_TENANT_SLUG).first()
    if not tenant:
        raise HTTPException(status_code=500, detail="Demo-Tenant nicht geseedet")
    return tenant.id


def require_internal(
    atlas_auth: str | None = Cookie(default=None),
    x_atlas_internal: str | None = Header(default=None),
) -> None:
    """Zugang zum internen Kurations-Bereich (Abschnitt 13.2, Punkt 4). Das ist
    geteiltes Atlas-Wissen, kein Kundengeheimnis -- deshalb KEINE Tenant-Filterung,
    sondern eine eigene Berechtigungsstufe neben dem Kunden-Login.

    Ist ATLAS_INTERNAL_TOKEN nicht gesetzt, bleibt es beim normalen Login wie bisher.
    Damit laesst sich die Trennung per Umgebungsvariable scharfschalten, ohne dass
    ein nicht konfiguriertes Deployment den internen Bereich verliert.
    """
    require_auth(atlas_auth)

    expected = os.getenv("ATLAS_INTERNAL_TOKEN")
    if not expected:
        return
    if not x_atlas_internal or not hmac.compare_digest(x_atlas_internal, expected):
        raise HTTPException(status_code=403, detail="Kein Zugriff auf den internen Bereich")
