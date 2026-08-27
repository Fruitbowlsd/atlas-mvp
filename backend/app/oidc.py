"""Microsoft Entra ID (OIDC) Anbindung -- Abschnitt 13.4.

Authlib statt msal, weil die Architektur laut 13.4 spaeter weitere Anbieter
(Google, Okta) aufnehmen koennen soll: Authlib ist anbieterunabhaengig, uebernimmt
Discovery, JWKS-Abruf und vor allem die Validierung des ID-Tokens (Signatur, iss,
aud, exp, nonce). Genau dieser Teil ist der sicherheitskritische, den man bei
einer Handimplementierung ueber httpx subtil falsch macht.
"""
import os

from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException

AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
# Muss in der Azure-App-Registrierung ZEICHENGENAU hinterlegt sein. Fuer lokale
# Entwicklung und Railway jeweils eine eigene URI dort eintragen; diese Variable
# waehlt aus, welche gesendet wird.
AZURE_REDIRECT_URI = os.getenv("AZURE_REDIRECT_URI")
# Wohin nach erfolgreichem Login weitergeleitet wird. Noetig, weil der Callback ein
# vollstaendiger Seitenwechsel ist: lokal landet der Nutzer sonst auf dem Backend-Port
# (8000) statt beim Vite-Dev-Server (5173), wo im Entwicklungsbetrieb das Frontend liegt.
POST_LOGIN_URL = os.getenv("ATLAS_POST_LOGIN_URL", "/")

_oauth: OAuth | None = None


def is_configured() -> bool:
    """SSO ist nur nutzbar, wenn die Anwendung vollstaendig konfiguriert ist. Sonst
    bleibt der Passwort-Weg der einzige -- besser als eine Weiterleitung ins Leere."""
    return all([AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID, AZURE_REDIRECT_URI])


def get_client():
    """Authlib-Client fuer Entra. Die Discovery-URL zeigt bewusst auf den KONKRETEN
    Verzeichnis-Tenant, nicht auf "common" -- damit gilt der Login von vornherein
    nur fuer die eigene Organisation."""
    global _oauth
    if not is_configured():
        raise HTTPException(status_code=503, detail="SSO ist nicht konfiguriert")

    if _oauth is None:
        _oauth = OAuth()
        _oauth.register(
            name="entra",
            client_id=AZURE_CLIENT_ID,
            client_secret=AZURE_CLIENT_SECRET,
            server_metadata_url=(
                f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/v2.0/.well-known/openid-configuration"
            ),
            client_kwargs={"scope": "openid email profile"},
        )
    return _oauth.entra


def email_from_claims(claims: dict) -> str | None:
    """E-Mail aus dem ID-Token. Entra liefert den Claim je nach Kontenart
    unterschiedlich -- "email" fehlt z.B. bei reinen Verzeichniskonten ohne
    gesetzte Mailadresse, dort traegt "preferred_username" die Adresse."""
    for claim in ("email", "preferred_username", "upn"):
        value = claims.get(claim)
        if value and "@" in value:
            return value.strip().lower()
    return None


def logout_url(post_logout_redirect: str) -> str:
    """Entra-Logout (OIDC end_session_endpoint). Ohne diesen Aufruf bliebe die
    Microsoft-Sitzung bestehen und der naechste Login-Versuch wuerde den Nutzer
    ohne Nachfrage sofort wieder anmelden."""
    from urllib.parse import urlencode

    base = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/logout"
    return f"{base}?{urlencode({'post_logout_redirect_uri': post_logout_redirect})}"
