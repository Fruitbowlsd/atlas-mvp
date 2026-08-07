"""Anthropic-API-Anbindung fuer Pipeline-Schritt 4 (Planungsdokument Abschnitt
11.2): Kategorisierung, Risiko-/Aufwandseinschaetzung und Kurzbeschreibung fuer
die vom klassischen Diff (Schritt 3, siehe diff.py) gefundenen neuen/geaenderten
Zeilen. Bekommt bewusst NUR diese Zeilen, nicht den kompletten Requirement-
Katalog -- der zentrale Kostenhebel aus 11.2 (>95% weniger Tokens als eine
Volltext-Analyse). Ergebnis ist immer ein Vorschlag (origin="ki_vorschlag",
status="entwurf"), der Kurator prueft/korrigiert ihn in der Kuratoren-UI
(Schritt 2b), bevor er live geht -- "System schlaegt vor, Mensch bestaetigt".
"""
import os

import anthropic

from .diff import RequirementDiffEntry

# Kleines, guenstiges Modell fuer die im MVP ausreichend einfache Kategorisierung
# (siehe 11.2: "kleineres Modell fuer einfache Kategorisierung, groesseres nur
# bei mehrdeutigen Faellen" -- die Ausbaustufe mit Modell-Eskalation ist bewusst
# nicht Teil dieser ersten Umsetzung).
MODEL = "claude-haiku-4-5-20251001"

_TOOL_NAME = "regulatorische_aenderungen_einschaetzen"
_CATEGORIES = ["neuer_prozess", "neues_pflichtfeld", "neuer_code", "neue_qualitaetsregel", "neuer_testfall"]
_LEVELS = ["hoch", "mittel", "niedrig"]

_TOOL_SCHEMA = {
    "name": _TOOL_NAME,
    "description": (
        "Schaetzt fuer jede uebergebene Requirement-Aenderung Kategorie, Risiko, "
        "Aufwand und eine Kurzbeschreibung fuer einen menschlichen Kurator."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "einschaetzungen": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "requirement_code": {"type": "string"},
                        "titel": {
                            "type": "string",
                            "description": "Kurzer, verstaendlicher Titel fuer die Kuratoren-Ansicht",
                        },
                        "kategorie": {"type": "string", "enum": _CATEGORIES},
                        "risiko": {"type": "string", "enum": _LEVELS},
                        "aufwand": {"type": "string", "enum": _LEVELS},
                        "beschreibung": {
                            "type": "string",
                            "description": "1-2 Saetze: was aendert sich fachlich, warum ist es relevant",
                        },
                    },
                    "required": ["requirement_code", "titel", "kategorie", "risiko", "aufwand", "beschreibung"],
                },
            },
        },
        "required": ["einschaetzungen"],
    },
}


class AiAnalysisError(RuntimeError):
    """Wird geworfen, wenn der Key fehlt, die API einen Fehler liefert oder die
    Antwort nicht das erwartete Format hat -- der Router uebersetzt das in einen
    502 fuer die Kuratoren-UI."""


def _entry_to_prompt_line(entry: RequirementDiffEntry) -> str:
    if entry.change_type == "neu":
        return f"- NEU | Code {entry.requirement_code} | PI {entry.pi_number or '-'} | Titel: {entry.title}"
    fields = ", ".join(entry.changed_fields) or "-"
    return (
        f"- GEAENDERT | Code {entry.requirement_code} | PI {entry.pi_number or '-'} | "
        f"Alter Titel: {entry.old_title!r} | Neuer Titel: {entry.title!r} | Geaenderte Felder: {fields}"
    )


def analyze_diff_entries(entries: list[RequirementDiffEntry]) -> list[dict]:
    """Ruft die Anthropic-API fuer die uebergebenen (bereits klassisch gefilterten,
    d.h. nur neue/geaenderte) Diff-Zeilen auf und liefert strukturierte
    Einschaetzungen als Liste von Dicts zurueck (ein Eintrag je Diff-Zeile)."""
    if not entries:
        return []

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise AiAnalysisError(
            "ANTHROPIC_API_KEY ist nicht gesetzt -- in backend/.env (lokal, mit "
            "--env-file gestartet) bzw. den Railway-Variablen hinterlegen."
        )

    lines = "\n".join(_entry_to_prompt_line(e) for e in entries)
    prompt = (
        "Du unterstuetzt einen Kurator bei der deutschen Marktkommunikation Gas "
        "(BNetzA/BDEW-Regelwerk, UTILMD/GeLi Gas). Unten stehen strukturell "
        "erkannte Aenderungen zwischen zwei Formatversionen -- bereits klassisch "
        "gefiltert, es sind ausschliesslich neue oder inhaltlich geaenderte "
        "Zeilen, keine unveraenderten. Schaetze fuer JEDE Zeile Kategorie, Risiko, "
        "Aufwand und schreibe eine kurze, fachlich praezise Beschreibung fuer die "
        "Kuratoren-Oberflaeche.\n\n" + lines
    )

    client = anthropic.Anthropic(api_key=api_key)
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            tools=[_TOOL_SCHEMA],
            tool_choice={"type": "tool", "name": _TOOL_NAME},
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.APIError as e:
        raise AiAnalysisError(f"Anthropic-API-Fehler: {e}") from e

    for block in response.content:
        if block.type == "tool_use" and block.name == _TOOL_NAME:
            return block.input.get("einschaetzungen", [])

    raise AiAnalysisError("Anthropic-Antwort enthielt keinen erwarteten Tool-Use-Block")
