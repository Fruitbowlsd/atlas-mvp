"""Login-Flow analog claude.ai (Abschnitt 13.4): erst E-Mail, dann -- abhaengig von
der Domain -- entweder Weiterleitung zum SSO-Anbieter oder ein Passwort-Feld."""
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from . import auth, models, oidc
from .database import get_db

router = APIRouter(prefix="/api", tags=["auth"])
# Die OIDC-Endpunkte liegen bewusst ausserhalb von /api: der Callback ist ein
# Seitenwechsel im Browser, keine XHR-Anfrage.
oidc_router = APIRouter(prefix="/auth", tags=["auth"])


class EmailCheckRequest(BaseModel):
    email: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login/check-email")
def check_email(payload: EmailCheckRequest, db: Session = Depends(get_db)):
    """Schritt 1 des Logins: entscheidet, was im zweiten Schritt angeboten wird.

    Gibt bewusst KEINE Auskunft darueber, ob die Adresse existiert -- sonst waere der
    Endpunkt eine Liste gueltiger Nutzerkonten. Unbekannte Adressen bekommen den
    Passwort-Weg angeboten und scheitern dann am Passwort.
    """
    tenant = auth.tenant_for_email(db, payload.email)

    if tenant and tenant.sso_provider == "entra" and oidc.is_configured():
        return {"mode": "sso", "provider": "entra", "tenant_name": tenant.name}
    if tenant and tenant.sso_provider == "entra":
        # Fuer den Tenant ist SSO hinterlegt, die Anwendung aber nicht konfiguriert.
        return {"mode": "sso_unavailable", "provider": "entra", "tenant_name": tenant.name}
    return {"mode": "password"}


@router.post("/login")
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = auth.find_user_by_email(db, payload.email)
    # Einheitliche Fehlermeldung fuer "kein Konto", "falsches Passwort" und
    # "SSO-Konto ohne Passwort" -- sonst liesse sich daraus ableiten, welche
    # Adressen existieren.
    if not user or not user.is_active or not auth.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="E-Mail oder Passwort ist falsch")

    auth.mark_logged_in(db, user)
    auth.set_session_cookie(response, user.id)
    return {"status": "ok", "email": user.email}


@router.get("/me")
def me(user: models.User | None = Depends(auth.get_optional_user)):
    """Ersetzt das fruehere /login/check. Liefert zusaetzlich die Identitaet, damit
    die Sidebar zeigen kann, wer angemeldet ist."""
    if not user:
        return {"authenticated": False}
    return {
        "authenticated": True,
        "email": user.email,
        "tenant_name": user.tenant.name if user.tenant else None,
        "is_sso_user": user.password_hash is None,
    }


@router.post("/logout")
def logout(response: Response, user: models.User | None = Depends(auth.get_optional_user)):
    """Meldet lokal ab. Bei SSO-Nutzern liefert die Antwort zusaetzlich die
    Entra-Logout-URL -- ohne die bliebe die Microsoft-Sitzung bestehen und der
    naechste Login-Versuch wuerde den Nutzer sofort wieder anmelden."""
    sso_logout_url = None
    if user and user.password_hash is None and oidc.is_configured():
        sso_logout_url = oidc.logout_url(oidc.POST_LOGIN_URL)

    auth.clear_session_cookie(response)
    return {"status": "ok", "sso_logout_url": sso_logout_url}


# --- OIDC ------------------------------------------------------------------

@oidc_router.get("/login")
async def sso_login(request: Request):
    client = oidc.get_client()
    try:
        return await client.authorize_redirect(request, oidc.AZURE_REDIRECT_URI)
    except Exception as e:  # noqa: BLE001
        # Haeufigster Fall beim Einrichten: falsche AZURE_TENANT_ID -- dann liefert
        # Microsoft schon das Discovery-Dokument nicht aus. Eine klare Meldung ist
        # hier deutlich hilfreicher als ein Stacktrace.
        raise HTTPException(
            status_code=502,
            detail=f"Microsoft-Anmeldung nicht erreichbar -- bitte AZURE_*-Variablen pruefen ({e})",
        )


@oidc_router.get("/callback")
async def sso_callback(request: Request, db: Session = Depends(get_db)):
    client = oidc.get_client()
    try:
        token = await client.authorize_access_token(request)
    except Exception as e:  # noqa: BLE001 -- Authlib wirft je nach Fehlerart unterschiedlich
        raise HTTPException(status_code=401, detail=f"SSO-Anmeldung fehlgeschlagen: {e}")

    claims = token.get("userinfo") or {}
    email = oidc.email_from_claims(claims)
    if not email:
        raise HTTPException(status_code=401, detail="ID-Token enthaelt keine E-Mail-Adresse")

    user = auth.find_user_by_email(db, email)
    if user is None:
        user = _provision_sso_user(db, email, claims)

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Dieses Konto ist deaktiviert")

    auth.mark_logged_in(db, user)
    response = RedirectResponse(url=oidc.POST_LOGIN_URL, status_code=302)
    auth.set_session_cookie(response, user.id)
    return response


def _provision_sso_user(db: Session, email: str, claims: dict) -> models.User:
    """Just-in-Time Provisioning (Abschnitt 13.4).

    Die Tenant-Zuordnung erfolgt ueber die Mail-Domain -- NIE ueber einen
    Default-Tenant. Waere hier ein Fallback, koennte ein fremder Nutzer in einem
    bestehenden Tenant landen und dessen Kundendaten sehen; das wuerde die gesamte
    Mandantentrennung aushebeln. Ohne passenden Tenant wird abgelehnt.
    """
    tenant = auth.tenant_for_email(db, email)
    if not tenant or tenant.sso_provider != "entra":
        raise HTTPException(
            status_code=403,
            detail="Fuer diese E-Mail-Domain ist kein Zugang eingerichtet",
        )

    # Das Verzeichnis muss auch wirklich das hinterlegte sein. Ohne diese Pruefung
    # koennte -- je nach Konfiguration der App-Registrierung -- ein Konto aus einem
    # fremden Microsoft-Verzeichnis einen Zugang bei uns erhalten.
    token_directory = claims.get("tid")
    if tenant.sso_tenant_id and token_directory != tenant.sso_tenant_id:
        raise HTTPException(status_code=403, detail="Anmeldung aus einem fremden Verzeichnis")

    user = models.User(email=email, password_hash=None, tenant_id=tenant.id, is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
