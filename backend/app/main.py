import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles

from .database import Base, engine, SessionLocal
from . import models  # noqa: F401  (stellt sicher, dass alle Modelle registriert sind)
from .migrations import run_light_migrations
from .seed_runner import run_seed
from .routers_auth import router as auth_router, oidc_router
from .routers_reference import router as reference_router
from .routers_assessments import router as assessments_router, customer_router
from .routers_import import router as import_router
from .routers_regulatory import router as regulatory_router, internal_router as regulatory_internal_router
from .routers_admin import router as admin_router

app = FastAPI(title="Atlas MVP - Energy Quality Assessment", version="0.1.0")

# CORS nur relevant, wenn Frontend und Backend getrennt gehostet werden
# (z.B. lokal via `npm run dev` auf Port 5173). Bei kombiniertem Deploy
# (Backend liefert das gebaute Frontend selbst aus) greift das ohnehin nicht.
ALLOWED_ORIGINS = os.getenv("ATLAS_ALLOWED_ORIGINS", "http://localhost:5173").split(",")

# Von Authlib fuer state/nonce des OIDC-Flows benoetigt -- kurzlebig und getrennt
# vom eigentlichen Anmelde-Cookie (siehe auth.py).
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("ATLAS_SESSION_SECRET", "atlas-dev-secret-change-me"),
    same_site="lax",
    https_only=os.getenv("ATLAS_COOKIE_SECURE", "false").lower() == "true",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,  # noetig, damit der Auth-Cookie mitgeschickt wird
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    run_light_migrations(engine)
    db = SessionLocal()
    try:
        run_seed(db)
    finally:
        db.close()


@app.get("/api/health")
def health():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(oidc_router)
app.include_router(reference_router)
app.include_router(assessments_router)
app.include_router(customer_router)
app.include_router(import_router)
app.include_router(regulatory_router)
app.include_router(regulatory_internal_router)
app.include_router(admin_router)

# Gebautes Frontend (falls vorhanden) unter "/" ausliefern -- so laesst sich
# das Projekt als EIN Service deployen (z.B. auf Railway), ohne separates
# Frontend-Hosting. Wird im Docker-Build nach app/static kopiert.
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    # Eigene Klasse statt des blanken StaticFiles: die App kennt mit /admin eine
    # echte URL ohne eigene Datei. Ohne diesen Rueckfall liefe ein Direktaufruf
    # oder ein Reload dort in einen 404.
    class SpaStaticFiles(StaticFiles):
        async def get_response(self, path: str, scope):
            try:
                return await super().get_response(path, scope)
            except StarletteHTTPException as exc:
                # Starlette WIRFT bei fehlenden Dateien, statt eine 404-Antwort
                # zurueckzugeben -- deshalb hier abfangen statt status_code pruefen.
                if exc.status_code != 404:
                    raise
                # API- und Auth-Pfade NICHT auf die App umbiegen: ein vertippter
                # Endpunkt soll ein ehrliches 404 liefern statt stillschweigend
                # HTML, was Fehler im Frontend schwer auffindbar machen wuerde.
                if path.startswith("api/") or path.startswith("auth/"):
                    raise
                return await super().get_response("index.html", scope)

    app.mount("/", SpaStaticFiles(directory=STATIC_DIR, html=True), name="static")
