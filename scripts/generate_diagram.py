#!/usr/bin/env python3
"""Erzeugt den generierten Teil von docs/class_diagram.md aus backend/app/models.py.

Das Script liest die SQLAlchemy-Modelle rein statisch per ``ast`` -- es importiert
weder ``app.database`` noch legt es eine Engine an. Dadurch laeuft es ohne
installierte Abhaengigkeiten und ohne Datenbank, was es fuer die GitHub Action
(.github/workflows/update_diagram.yml) unkritisch macht.

Ersetzt wird ausschliesslich der Block zwischen den Markern

    <!-- BEGIN GENERATED: class-diagram -->
    <!-- END GENERATED: class-diagram -->

Alles andere in class_diagram.md -- Lesehilfe, Uebersicht, geplante Entitaeten,
Umsetzungsstand, fachliche Anmerkungen -- bleibt handgepflegt.

Aufruf:
    python scripts/generate_diagram.py            # schreibt die Datei
    python scripts/generate_diagram.py --check    # Exit 1, wenn veraltet
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MODELS_PATH = REPO_ROOT / "backend" / "app" / "models.py"
DIAGRAM_PATH = REPO_ROOT / "docs" / "class_diagram.md"

BEGIN_MARKER = "<!-- BEGIN GENERATED: class-diagram -->"
END_MARKER = "<!-- END GENERATED: class-diagram -->"

# SQLAlchemy-Typ -> Kurzform im Diagramm. Bewusst die knappen Namen aus der
# Lesehilfe von class_diagram.md, nicht die SQLAlchemy-Klassennamen.
TYPE_MAP = {
    "Integer": "int",
    "String": "str",
    "Text": "text",
    "Boolean": "bool",
    "Float": "float",
    "DateTime": "datetime",
    "Date": "date",
    "Numeric": "float",
    "JSON": "json",
}

# Fachliche Gruppierung der Entitaeten (Abschnitt 13.1 der Planung). Neue Modelle,
# die hier fehlen, landen sichtbar in G0 -- der Diff macht dann darauf aufmerksam,
# dass die Zuordnung nachgetragen werden muss.
GROUPS: list[tuple[str, str, list[str]]] = [
    (
        "G1_Mandanten_und_Auth",
        "Gruppe 1 — Mandanten & Auth (Abschnitt 13)",
        ["Tenant", "User"],
    ),
    (
        "G2_Kundendaten",
        "Gruppe 2 — Kundendaten (mandantengetrennt, tragen tenant_id)",
        ["Customer", "Assessment", "AssessmentRequirement", "ScoreResult", "Finding"],
    ),
    (
        "G3_Regulatorische_Referenzdaten",
        "Gruppe 3 — Regulatorische Referenzdaten (geteilt, kein tenant_id)",
        [
            "RegulatoryVersion",
            "RegulatoryChange",
            "Requirement",
            "ProcessIdentifier",
            "ProcessGroup",
        ],
    ),
    (
        "G3b_Technology_Intelligence",
        "Gruppe 3b — Technology Intelligence / Ebene 2",
        [
            "TechnologySystem",
            "TechnologyReleaseNote",
            "RegulatoryChangeTechnologyMapping",
        ],
    ),
    (
        "G4_Wissensbasis_EDIFACT",
        "Gruppe 4 — Wissensbasis EDIFACT (Abschnitt 14.2)",
        [
            "MessageDefinition",
            "MessageSegment",
            "MessageField",
            "MessageFieldCodeList",
            "CodeList",
            "CodeListEntry",
        ],
    ),
    (
        "G5_Testkonstellationen",
        "Gruppe 5 — Testkonstellationen (Abschnitt 14.2)",
        ["Testkonstellation", "TestkonstellationSchritt"],
    ),
]

UNGROUPED_KEY = "G0_Nicht_zugeordnet"
UNGROUPED_TITLE = "Gruppe 0 — noch keiner Gruppe zugeordnet (bitte in GROUPS nachtragen)"


class Column:
    def __init__(self, name: str, type_name: str, fk_table: str | None, nullable: bool):
        self.name = name
        self.type_name = type_name
        self.fk_table = fk_table
        self.nullable = nullable


class Model:
    def __init__(self, class_name: str, table_name: str):
        self.class_name = class_name
        self.table_name = table_name
        self.columns: list[Column] = []


def _type_name(node: ast.expr) -> str:
    """Erster Positionsparameter von Column() -> Kurzform. String(50) -> str."""
    if isinstance(node, ast.Name):
        return TYPE_MAP.get(node.id, node.id.lower())
    if isinstance(node, ast.Call):
        return _type_name(node.func)
    if isinstance(node, ast.Attribute):
        return TYPE_MAP.get(node.attr, node.attr.lower())
    return "?"


def _foreign_key_table(call: ast.Call) -> str | None:
    """Sucht ForeignKey("tabelle.spalte") in den Argumenten von Column()."""
    for arg in call.args:
        if (
            isinstance(arg, ast.Call)
            and isinstance(arg.func, ast.Name)
            and arg.func.id == "ForeignKey"
            and arg.args
            and isinstance(arg.args[0], ast.Constant)
            and isinstance(arg.args[0].value, str)
        ):
            return arg.args[0].value.split(".", 1)[0]
    return None


def _is_nullable(call: ast.Call) -> bool:
    """nullable=False oder primary_key=True bedeuten Pflichtfeld."""
    for kw in call.keywords:
        if kw.arg == "primary_key" and isinstance(kw.value, ast.Constant) and kw.value.value:
            return False
        if kw.arg == "nullable" and isinstance(kw.value, ast.Constant):
            return bool(kw.value.value)
    return True


def parse_models(path: Path) -> list[Model]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    models: list[Model] = []

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        if not any(isinstance(b, ast.Name) and b.id == "Base" for b in node.bases):
            continue

        table_name = ""
        columns: list[Column] = []

        for stmt in node.body:
            if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1:
                continue
            target = stmt.targets[0]
            if not isinstance(target, ast.Name):
                continue

            if target.id == "__tablename__" and isinstance(stmt.value, ast.Constant):
                table_name = str(stmt.value.value)
                continue

            # Nur Column(...) uebernehmen -- relationship(...) ergibt sich aus den FKs.
            if (
                isinstance(stmt.value, ast.Call)
                and isinstance(stmt.value.func, ast.Name)
                and stmt.value.func.id == "Column"
            ):
                call = stmt.value
                type_name = _type_name(call.args[0]) if call.args else "?"
                columns.append(
                    Column(target.id, type_name, _foreign_key_table(call), _is_nullable(call))
                )

        if not table_name:
            continue

        model = Model(node.name, table_name)
        model.columns = columns
        models.append(model)

    return models


def _grouped(models: list[Model]) -> list[tuple[str, str, list[Model]]]:
    by_name = {m.class_name: m for m in models}
    used: set[str] = set()
    result: list[tuple[str, str, list[Model]]] = []

    for key, title, class_names in GROUPS:
        members = [by_name[n] for n in class_names if n in by_name]
        used.update(m.class_name for m in members)
        if members:
            result.append((key, title, members))

    leftovers = [m for m in models if m.class_name not in used]
    if leftovers:
        result.append((UNGROUPED_KEY, UNGROUPED_TITLE, leftovers))

    return result


def _relations(models: list[Model]) -> list[str]:
    table_to_class = {m.table_name: m.class_name for m in models}
    lines: list[str] = []

    for model in models:
        for column in model.columns:
            if not column.fk_table:
                continue
            target = table_to_class.get(column.fk_table)
            if target is None:
                continue
            target_card = "0..1" if column.nullable else "1"
            lines.append(
                f'    {model.class_name} "0..*" --> "{target_card}" '
                f"{target} : {column.name}"
            )

    return lines


def render(models: list[Model]) -> str:
    separator = "    %% " + "=" * 69
    out: list[str] = ["```mermaid", "classDiagram", "    direction TB"]

    for key, title, members in _grouped(models):
        out += ["", separator, f"    %% {title}", separator, f"    namespace {key} {{"]
        for index, model in enumerate(members):
            if index:
                out.append("")
            out.append(f"        class {model.class_name} {{")
            for column in model.columns:
                out.append(f"            +{column.type_name} {column.name}")
            out.append("        }")
        out.append("    }")

    out += [
        "",
        separator,
        "    %% Beziehungen — aus den ForeignKey-Spalten abgeleitet",
        separator,
    ]
    out += _relations(models)
    out.append("```")

    return "\n".join(out)


def splice(document: str, block: str) -> str:
    start = document.find(BEGIN_MARKER)
    end = document.find(END_MARKER)
    if start == -1 or end == -1 or end < start:
        raise SystemExit(
            f"Marker {BEGIN_MARKER} / {END_MARKER} nicht (oder in falscher "
            f"Reihenfolge) in {DIAGRAM_PATH.relative_to(REPO_ROOT)} gefunden."
        )
    head = document[: start + len(BEGIN_MARKER)]
    tail = document[end:]
    return f"{head}\n\n{block}\n\n{tail}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Nichts schreiben, Exit-Code 1 wenn das Diagramm veraltet ist.",
    )
    args = parser.parse_args()

    if not MODELS_PATH.exists():
        raise SystemExit(f"Modelldatei nicht gefunden: {MODELS_PATH}")
    if not DIAGRAM_PATH.exists():
        raise SystemExit(f"Diagrammdatei nicht gefunden: {DIAGRAM_PATH}")

    models = parse_models(MODELS_PATH)
    if not models:
        raise SystemExit(f"Keine SQLAlchemy-Modelle in {MODELS_PATH} gefunden.")

    current = DIAGRAM_PATH.read_text(encoding="utf-8")
    updated = splice(current, render(models))

    if args.check:
        if current != updated:
            print("docs/class_diagram.md ist veraltet — bitte generate_diagram.py laufen lassen.")
            return 1
        print(f"docs/class_diagram.md ist aktuell ({len(models)} Entitaeten).")
        return 0

    if current == updated:
        print(f"docs/class_diagram.md unveraendert ({len(models)} Entitaeten).")
        return 0

    DIAGRAM_PATH.write_text(updated, encoding="utf-8")
    print(f"docs/class_diagram.md aktualisiert ({len(models)} Entitaeten).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
