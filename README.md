# Atlas MVP — Energy Quality Assessment (Lieferbeginn Gas)

Kleines, lauffähiges Fullstack-MVP für die Geschäftsführungs-Demo: bewertet die
Prozessqualität eines Gaslieferanten für den Prozess **Lieferbeginn Gas**
(GeLi Gas 2.0 / UTILMD Gas G1.1, Konsultationsstand 01.08.2025) anhand von
133 Requirements über 16 Prüfidentifikatoren (PIs), getrennt nach SLP/RLM.

Zwei Kennzahlen werden getrennt ausgewiesen:
- **Regulatorischer Abdeckungsgrad** — wie vollständig ist der relevante Soll-Katalog adressiert?
- **Qualitätsgrad** — wie gut sind die unterstützten Fälle implementiert, getestet, nachgewiesen?

## Schnellstart (Docker)

```bash
docker compose up --build
```

- Frontend: http://localhost:8080
- Backend-API: http://localhost:8000 (Swagger-Doku unter `/docs`)

Beim ersten Start werden die Referenzdaten (Prozessgruppen, PIs, Requirements)
und ein Demo-Kunde ("Demo Gaslieferant GmbH") mit bewusst eingebauten Lücken
automatisch geseedet.

## Deployment auf Railway (für Demos)

Das Projekt lässt sich als **ein einziger Service** deployen — das Root-`Dockerfile`
baut das Frontend und liefert es zusammen mit dem Backend aus einem Container aus.

1. Projekt auf GitHub pushen:
   ```bash
   cd atlas-mvp
   git init && git add . && git commit -m "Atlas MVP"
   # Repo auf GitHub anlegen, dann:
   git remote add origin <dein-repo-url>
   git push -u origin main
   ```
2. Auf [railway.app](https://railway.app) einloggen → **New Project** → **Deploy from GitHub repo**
   → dein Repo auswählen. Railway erkennt das `Dockerfile` im Root automatisch.
3. Unter **Variables** im Railway-Service setzen:
   - `ATLAS_DEMO_PASSWORD` — das Passwort für die Login-Seite (Pflicht, sonst gilt der unsichere Default)
   - `ATLAS_SESSION_SECRET` — ein beliebiger zufälliger String (Pflicht für echte Sicherheit)
   - `ATLAS_COOKIE_SECURE` — auf `true` setzen (Railway läuft über HTTPS)
4. Unter **Settings → Networking** auf **Generate Domain** klicken — das ist die URL, die du deinem Partner schickst.

**Zur SQLite-Datenbank:** Ohne extra konfiguriertes Volume ist das Dateisystem auf
Railway bei jedem Redeploy leer — das ist für diese Demo aber kein Problem, weil
die Referenzdaten und der Demo-Kunde beim Start automatisch neu geseedet werden
(`seed_runner.py`). Neu angelegte Assessments gehen bei einem Redeploy allerdings
verloren.

## Passwortschutz

Die gesamte App (Frontend-Zugriff auf Daten + API) ist hinter einer Login-Seite
geschützt. Das Passwort wird über die Umgebungsvariable `ATLAS_DEMO_PASSWORD`
gesetzt (lokal per `.env`/Shell-Variable, auf Railway über die Variables-Ansicht).
Ohne gültigen Login-Cookie antwortet die API mit `401`.

**Wichtig:** Das ist ein einfacher, für eine Demo ausreichender Schutz (ein
gemeinsames Passwort, signierter Cookie) — kein vollwertiges Benutzer-/Rechte-
system. Für den produktiven Einsatz mit echten Kundendaten wäre das durch
richtiges Auth (z.B. OAuth, einzelne Benutzerkonten) zu ersetzen.

## Lokale Entwicklung ohne Docker

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --env-file .env
```

`--env-file .env` laedt eine lokale `backend/.env`-Datei (z.B. fuer
`ANTHROPIC_API_KEY`, siehe [.env.example](backend/.env.example)) in die
Prozessumgebung -- ohne das Flag wird `.env` **nicht** automatisch gelesen,
nur echte Shell-/Systemvariablen. Auf Railway betrifft das nicht: dort werden
Variablen direkt in die Prozessumgebung injiziert.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Das Frontend läuft dann unter http://localhost:5173 und proxied `/api`-Aufrufe
automatisch an `http://localhost:8000` (siehe `vite.config.ts`).

## Demo-Ablauf

1. Frontend öffnen — lädt automatisch das Assessment des Demo-Kunden.
2. Regulatorischer Abdeckungsgrad und Qualitätsgrad sind oben als Score-Cards zu sehen.
3. Heatmap zeigt die Ampel je Prozessgruppe (Stornierung ist bewusst "rot" — geringste Abdeckung).
4. In den Akkordeons lässt sich der Status jeder Anforderung live ändern
   (Umsetzung / Test / Nachweis) — Änderungen werden sofort gespeichert.
5. "Bewertung neu berechnen" aktualisiert Score, Heatmap und Findings serverseitig.
6. Findings-Liste unten zeigt automatisch generierte Lücken mit Empfehlung.

## Projektstruktur

```text
atlas-mvp/
├── backend/           FastAPI, SQLAlchemy, SQLite (Standard) oder Postgres via DATABASE_URL
│   └── app/
│       ├── main.py            Entry-Point, CORS, Seeding beim Start
│       ├── models.py          SQLAlchemy-Modelle
│       ├── schemas.py         Pydantic Request/Response-Schemas
│       ├── seed_data.py       Referenzkatalog: Prozessgruppen, PIs, Requirements
│       ├── seed_runner.py     Seed-Logik inkl. regelbasierter Demo-Statusvergabe
│       ├── services.py        Scoring, Findings-Generierung, Heatmap
│       ├── routers_reference.py     GET-Endpunkte für Referenzdaten
│       └── routers_assessments.py   Assessment-CRUD, Status-Update, Berechnung
└── frontend/           React + TypeScript + Vite
    └── src/
        ├── App.tsx             Hauptseite (Scores, Heatmap, Accordions, Findings)
        ├── api/client.ts       zentrale API-Schicht
        ├── types.ts            TypeScript-Typen (spiegeln die Backend-Schemas)
        └── components/         ScoreCard, Heatmap, ProcessGroupAccordion, PiCard, ...
```

## Bekannte Vereinfachungen im MVP (bewusst, siehe Planungsdokument)

- Umsetzungsstatus ist binär (implementiert / nicht implementiert), keine Teilerfüllung.
- Evidence ist ein reines Text-/URL-Feld, kein echter Datei-Upload.
- Regel-Engine für Relevanzableitung ist im Code (nicht als separate JSON-Datei) hinterlegt —
  lässt sich bei Bedarf leicht auslagern.
- Kein Login/Benutzerverwaltung — für die Demo bewusst offen gehalten.
- "Aktualität" (eine der vier Qualitäts-Unterdimensionen) ist im MVP ein fixer Wert (92 %)
  statt einer echten Prüfung gegen den Formatversions-Stichtag.
- Die nächste Granularitätsstufe (feldweise Muss-/Soll-/Kann-Prüfung je UTILMD-Segment)
  ist bewusst nicht Teil dieses MVP.

## Nächste Ausbaustufen

Siehe `MVP_Planung_Lieferbeginn_Gas.md` (Arbeitspaket-Liste) für den vollständigen Fahrplan,
u.a. PostgreSQL-Wechsel, echte Evidence-Uploads, Mandantenfähigkeit, weitere Prozesse
(Strom/GPKE), automatisches Mapping von Kundentestfällen.
