from datetime import datetime

# Seed-Datensatz fuer das MVP: Lieferbeginn Gas (GeLi Gas 2.0 / UTILMD Gas G1.1,
# Konsultationsstand 01.08.2025).
#
# Erweiterter Stand: vollstaendiger Testfallkatalog auf Basis der Atlas-Analyse
# des BDEW-UTILMD-AHB Gas 1.1 (16 PIs, ~133 Requirements, SLP/RLM getrennt).
# Nicht ausmodelliert ist die naechste Granularitaetsstufe (feldweise Muss-/
# Soll-/Kann-Pruefung je UTILMD-Segment) - das waere ein vollstaendiger
# Nachrichtenvalidierungskatalog und bewusst nicht Teil dieses MVP.

REGULATORY_VERSION = {
    "name": "GeLi Gas 2.0 / UTILMD Gas G1.1 (gültig ab 01.04.2026)",
    "sector": "gas",
    "status": "verbindlich",
    "source_reference": "BDEW/EDI@Energy, Formatumstellung zum 01.04.2026",
    # Stichtag der letzten Formatumstellung. Vorher stand hier gar kein Datum und der
    # Katalog war als Konsultationsstand 01.08.2025 gefuehrt -- also als Entwurf,
    # obwohl es der geltende Stand ist. Mit gesetztem valid_from leitet sich der
    # Assessment-Typ direkt aus dem Datum ab statt aus dem "gilt seit jeher"-Fallback.
    "valid_from": datetime(2026, 4, 1),
    "is_active": True,  # Default-Referenzkatalog fuer neue Assessments (Abschnitt 11.7)
}

PROCESS_GROUPS = [
    {"code": "registration", "name": "Anmeldung", "sequence": 1},
    {"code": "deregistration_request", "name": "Abmeldeanfrage", "sequence": 2},
    {"code": "information_messages", "name": "Informationsmeldungen", "sequence": 3},
    {"code": "cancellation", "name": "Stornierung", "sequence": 4},
    {"code": "business_data", "name": "Geschaeftsdaten", "sequence": 5},
    {"code": "portfolio_reconciliation", "name": "Bestandsabgleich", "sequence": 6},
]

# (pi_number, name, sender, receiver, group_code, criticality)
PROCESS_IDENTIFIERS = [
    ("44001", "Anmeldung Netznutzung", "LF", "NB", "registration", "kritisch"),
    ("44002", "Bestaetigung Anmeldung", "NB", "LF", "registration", "kritisch"),
    ("44003", "Ablehnung Anmeldung", "NB", "LF", "registration", "kritisch"),
    ("44010", "Abmeldeanfrage", "NB", "LF_alt", "deregistration_request", "hoch"),
    ("44011", "Bestaetigung Abmeldeanfrage", "LF_alt", "NB", "deregistration_request", "hoch"),
    ("44012", "Ablehnung Abmeldeanfrage", "LF_alt", "NB", "deregistration_request", "hoch"),
    ("44036", "Information bestehende Zuordnung", "NB", "LF", "information_messages", "mittel"),
    ("44037", "Information Beendigung der Zuordnung", "NB", "LF", "information_messages", "mittel"),
    ("44038", "Aufhebung zukuenftiger Zuordnung", "NB", "LF", "information_messages", "mittel"),
    ("44022", "Stornierungsanfrage", "LF", "NB", "cancellation", "mittel"),
    ("44023", "Bestaetigung Stornierung", "NB", "LF", "cancellation", "mittel"),
    ("44024", "Ablehnung Stornierung", "NB", "LF", "cancellation", "mittel"),
    ("44035", "Antwort auf Geschaeftsdatenanfrage", "NB", "LF", "business_data", "niedrig"),
    ("44019", "Bestandsliste", "NB", "LF", "portfolio_reconciliation", "niedrig"),
    ("44020", "Aenderungsmeldung zur Bestandsliste", "LF", "NB", "portfolio_reconciliation", "niedrig"),
    ("44021", "Antwort auf Aenderungsmeldung", "NB", "LF", "portfolio_reconciliation", "niedrig"),
]

WEIGHT_BY_CRITICALITY = {"kritisch": 3.0, "hoch": 2.0, "mittel": 1.5, "niedrig": 1.0}

# (code, title, pi_number, transaction_reason, response_code, criticality, slp, rlm)
REQUIREMENTS = [
    # --- PI 44001: gemeinsame Testfaelle SLP+RLM (15) ---
    ("LB-44001-E01", "Anmeldung wegen Ein-/Auszug bzw. Umzug", "44001", "E01", None, "kritisch", True, True),
    ("LB-44001-E02", "Anmeldung wegen Einzug in Neuanlage", "44001", "E02", None, "hoch", True, True),
    ("LB-44001-E03", "Anmeldung wegen Lieferantenwechsel (Kernszenario)", "44001", "E03", None, "kritisch", True, True),
    ("LB-44001-ZD2", "Lieferbeginn und Abmeldung aus Ersatzversorgung", "44001", "ZD2", None, "hoch", True, True),
    ("LB-44001-Z17", "Befristete Anmeldung mit Vertragsende", "44001", "Z17", None, "mittel", True, True),
    ("LB-44001-UNBEFRISTET", "Unbefristete Anmeldung ohne Vertragsende", "44001", None, None, "niedrig", True, True),
    ("LB-44001-ZUKUENFTIG", "Zukuenftiger Lieferbeginn", "44001", None, None, "mittel", True, True),
    ("LB-44001-RUECKWIRKEND", "Rueckwirkender Lieferbeginn mit Zaehlerstandankuendigung", "44001", None, None, "hoch", True, True),
    ("LB-44001-BK-PRIO", "Anmeldung mit mehreren Bilanzkreisen und Priorisierung", "44001", None, None, "mittel", True, True),
    ("LB-44001-NNV-KUNDE", "Netznutzungsvertrag Kunde-NB", "44001", None, None, "niedrig", True, True),
    ("LB-44001-NNV-LF", "Netznutzungsvertrag LF-NB", "44001", None, None, "niedrig", True, True),
    ("LB-44001-ZAHLUNG-KUNDE", "Zahlung der Netznutzung durch Kunden", "44001", None, None, "niedrig", True, True),
    ("LB-44001-ZAHLUNG-LF", "Zahlung der Netznutzung durch Lieferanten", "44001", None, None, "niedrig", True, True),
    ("LB-44001-Z12", "Identifikationslogik ueber Marktlokations-ID", "44001", None, "Z12", "hoch", True, True),
    ("LB-44001-Z13", "Identifikationslogik ueber vollstaendige Identifikationsdaten", "44001", None, "Z13", "hoch", True, True),

    # --- PI 44001: SLP-spezifische Varianten (17) ---
    ("LB-SLP-01", "Prognosegrundlage Profile (ZA6)", "44001", None, "ZA6", "mittel", True, False),
    ("LB-SLP-02", "Veranschlagte Jahresmenge vorhanden", "44001", None, None, "mittel", True, False),
    ("LB-SLP-03", "TUM-Kundenwert vorhanden", "44001", None, None, "mittel", True, False),
    ("LB-SLP-04", "TUM-Kundenwert und Jahresmenge - Prioritaet geprueft", "44001", None, None, "mittel", True, False),
    ("LB-SLP-05", "Synthetisches Lastprofil", "44001", None, None, "mittel", True, False),
    ("LB-SLP-06", "Analytisches Lastprofil", "44001", None, None, "mittel", True, False),
    ("LB-SLP-07", "Lastprofilcode durch NB vergeben", "44001", None, None, "mittel", True, False),
    ("LB-SLP-08", "Klimazone vorhanden", "44001", None, None, "niedrig", True, False),
    ("LB-SLP-09", "Temperaturmessstelle vorhanden", "44001", None, None, "niedrig", True, False),
    ("LB-SLP-10", "Haushaltskunde nach EnWG", "44001", None, None, "niedrig", True, False),
    ("LB-SLP-11", "Kein Haushaltskunde nach EnWG (Gewerbe)", "44001", None, None, "niedrig", True, False),
    ("LB-SLP-12", "Konzessionsabgabe Tarifkunde", "44001", None, None, "niedrig", True, False),
    ("LB-SLP-13", "Konzessionsabgabe Kochen/Warmwasser", "44001", None, None, "niedrig", True, False),
    ("LB-SLP-14", "Sondervertragskunde", "44001", None, None, "niedrig", True, False),
    ("LB-SLP-15", "Gemeinderabatt vorhanden", "44001", None, None, "niedrig", True, False),
    ("LB-SLP-16", "Manuell ausgelesener Gaszaehler", "44001", None, None, "niedrig", True, False),
    ("LB-SLP-17", "Fernauslesbarer Gaszaehler", "44001", None, None, "niedrig", True, False),

    # --- PI 44001: RLM-spezifische Varianten (19) ---
    ("LB-RLM-01", "Prognosegrundlage Werte (ZC0)", "44001", None, "ZC0", "hoch", False, True),
    ("LB-RLM-02", "Fallgruppe RLM Tagesregime", "44001", None, None, "hoch", False, True),
    ("LB-RLM-03", "Fallgruppe RLM Stundenregime", "44001", None, None, "hoch", False, True),
    ("LB-RLM-04", "Start Abrechnungsjahr bei Jahresleistungspreis", "44001", None, None, "mittel", False, True),
    ("LB-RLM-05", "Abrechnungsvariante Arbeitspreis/Leistungspreis", "44001", None, None, "mittel", False, True),
    ("LB-RLM-06", "Abrechnungsvariante Arbeitspreis/Grundpreis", "44001", None, None, "mittel", False, True),
    ("LB-RLM-07", "Messdatenregistriergeraet vorhanden", "44001", None, None, "hoch", False, True),
    ("LB-RLM-08", "Mengenumwerter vorhanden", "44001", None, None, "hoch", False, True),
    ("LB-RLM-09", "Temperaturmengenumwerter", "44001", None, None, "mittel", False, True),
    ("LB-RLM-10", "Zustandsmengenumwerter", "44001", None, None, "mittel", False, True),
    ("LB-RLM-11", "Dichtemengenumwerter", "44001", None, None, "mittel", False, True),
    ("LB-RLM-12", "Korrekte Beziehung Zaehler-Mengenumwerter", "44001", None, None, "hoch", False, True),
    ("LB-RLM-13", "OBIS-Daten des Mengenumwerters", "44001", None, None, "mittel", False, True),
    ("LB-RLM-14", "Mehrere Messlokationen", "44001", None, None, "mittel", False, True),
    ("LB-RLM-15", "H-Gas", "44001", None, None, "niedrig", False, True),
    ("LB-RLM-16", "L-Gas", "44001", None, None, "niedrig", False, True),
    ("LB-RLM-17", "Hochdruck", "44001", None, None, "niedrig", False, True),
    ("LB-RLM-18", "Mitteldruck", "44001", None, None, "niedrig", False, True),
    ("LB-RLM-19", "Niederdruck", "44001", None, None, "niedrig", False, True),

    # --- PI 44002: Bestaetigung (14) ---
    ("LB-44002-01", "E15 - Zustimmung ohne Korrektur", "44002", None, "E15", "kritisch", True, True),
    ("LB-44002-02", "Z01 - Aenderung Netznutzungsbeginn", "44002", None, "Z01", "hoch", True, True),
    ("LB-44002-03", "Z01 - Aenderung Bilanzierungsbeginn", "44002", None, "Z01", "hoch", True, True),
    ("LB-44002-04", "Z01 - geaendertes Ende bei befristeter Anmeldung", "44002", None, "Z01", "mittel", True, True),
    ("LB-44002-05", "Z43 - Korrektur Bilanzkreis", "44002", None, "Z43", "hoch", True, True),
    ("LB-44002-06", "Z43 - Korrektur Prognosegrundlage", "44002", None, "Z43", "hoch", True, True),
    ("LB-44002-07", "Z44 - Korrektur nicht bilanzierungsrelevanter Daten", "44002", None, "Z44", "mittel", True, True),
    ("LB-44002-08", "Z43 und Z44 gemeinsam", "44002", None, "Z43+Z44", "mittel", True, True),
    ("LB-44002-09", "Z01 und Z44 gemeinsam", "44002", None, "Z01+Z44", "mittel", True, True),
    ("LB-44002-10", "Korrigierte gefuellte Felder werden uebernommen", "44002", None, None, "kritisch", True, True),
    ("LB-44002-11", "Leere Felder bestaetigen nicht die urspruenglichen Werte", "44002", None, None, "kritisch", True, True),
    ("LB-44002-SLP-01", "Korrektur Jahresmenge/Lastprofil", "44002", None, None, "mittel", True, False),
    ("LB-44002-RLM-01", "Korrektur RLM-Fallgruppe", "44002", None, None, "hoch", False, True),
    ("LB-44002-RLM-02", "Korrektur Mess-/Abrechnungsdaten", "44002", None, None, "hoch", False, True),

    # --- PI 44003: Ablehnung, ein Fall je Code (12) ---
    ("LB-44003-E14", "Ablehnung Sonstiges", "44003", None, "E14", "mittel", True, True),
    ("LB-44003-E17", "Ablehnung wegen Fristueberschreitung", "44003", None, "E17", "hoch", True, True),
    ("LB-44003-Z08", "Ablehnung: Transaktion bereits stattgefunden", "44003", None, "Z08", "mittel", True, True),
    ("LB-44003-Z09", "Ablehnung: Transaktionsgrund unplausibel", "44003", None, "Z09", "mittel", True, True),
    ("LB-44003-Z14", "Ablehnung: Doppelmeldung", "44003", None, "Z14", "mittel", True, True),
    ("LB-44003-Z35", "Ablehnung der Abmeldeanfrage", "44003", None, "Z35", "hoch", True, True),
    ("LB-44003-ZC5", "Ablehnung: andere Anmeldung in Bearbeitung", "44003", None, "ZC5", "hoch", True, True),
    ("LB-44003-ZE2", "Ablehnung wegen Kapazitaetsproblem", "44003", None, "ZE2", "mittel", False, True),
    ("LB-44003-A16", "Ablehnung: keine Teilnahme an Marktkommunikation", "44003", None, "A16", "niedrig", True, True),
    ("LB-44003-A17", "Ablehnung: Mehrfachidentifizierung", "44003", None, "A17", "niedrig", True, True),
    ("LB-44003-A03", "Ablehnung: keine Identifizierung", "44003", None, "A03", "niedrig", True, True),
    ("LB-44003-A04", "Ablehnung: Marktlokation nicht mehr im Netzgebiet", "44003", None, "A04", "niedrig", True, True),
    # E13 nach SLP/RLM getrennt statt eines gemeinsamen Falls
    ("LB-44003-E13-SLP", "Ablehnung wegen Bilanzierungsproblem (SLP)", "44003", None, "E13", "hoch", True, False),
    ("LB-44003-E13-RLM", "Ablehnung wegen Bilanzierungsproblem (RLM)", "44003", None, "E13", "hoch", False, True),
    # zusaetzliche fachliche Testvarianten
    ("LB-44003-E14-BEMERKUNG", "E14 mit verpflichtender verstaendlicher Bemerkung", "44003", None, "E14", "mittel", True, True),
    ("LB-44003-ZC5-INBEARBEITUNG", "ZC5 mit Lieferbeginndatum der laufenden Anmeldung", "44003", None, "ZC5", "hoch", True, True),
    ("LB-44003-ZC5-NAECHSTE", "ZC5 mit Datum fuer naechste Bearbeitung", "44003", None, "ZC5", "hoch", True, True),
    ("LB-44003-ZC5-PFLICHT-FEHLT", "ZC5 ohne Pflichtdatum fuehrt zu Fehler", "44003", None, "ZC5", "hoch", True, True),
    ("LB-44003-Z35-G0009", "Z35 mit eingebetteter Antwort aus G_0009", "44003", None, "Z35", "hoch", True, True),
    ("LB-44003-Z35-REFERENZ", "Z35 mit korrekter Referenz auf Abmeldeanfrage", "44003", None, "Z35", "hoch", True, True),
    ("LB-44003-A03-REDUZIERT", "A03 mit zulaessigem reduziertem Identifikationsumfang", "44003", None, "A03", "niedrig", True, True),

    # --- PI 44010-44012: Abmeldeanfrage (13) ---
    ("LB-44010-01", "NB sendet Abmeldeanfrage an Altlieferant", "44010", None, None, "hoch", True, True),
    ("LB-44010-02", "Korrekte Marktlokation in Abmeldeanfrage", "44010", None, None, "hoch", True, True),
    ("LB-44010-03", "Korrekter Neulieferant als beteiligter Marktpartner", "44010", None, None, "mittel", True, True),
    ("LB-44010-04", "Kundenname aus Anmeldung wird uebernommen", "44010", None, None, "mittel", True, True),
    ("LB-44011-01", "Altlieferant bestaetigt Abmeldeanfrage", "44011", None, None, "hoch", True, True),
    ("LB-44011-02", "Antwort referenziert Vorgangsnummer der Abmeldeanfrage", "44011", None, None, "hoch", True, True),
    ("LB-44011-03", "Bestaetigtes Ende wird korrekt verarbeitet", "44011", None, None, "mittel", True, True),
    ("LB-44012-01", "Altlieferant lehnt Abmeldeanfrage ab", "44012", None, None, "hoch", True, True),
    ("LB-44012-02", "Jeder relevante Code aus G_0009 wird verarbeitet", "44012", None, None, "hoch", True, True),
    ("LB-44012-03", "Ablehnung Sonstiges mit Bemerkung", "44012", None, "E14", "mittel", True, True),
    ("LB-44012-04", "Ablehnung wird ueber Z35 in PI 44003 weitergegeben", "44012", None, None, "kritisch", True, True),
    ("LB-44012-05", "Eingebetteter Drittmarktpartner-Code bleibt erhalten", "44012", None, None, "hoch", True, True),
    ("LB-44012-06", "Verspaetete oder fehlende Antwort wird korrekt behandelt", "44012", None, None, "mittel", True, True),

    # --- PI 44036-44038: Informationsmeldungen (10) ---
    ("LB-44036-01", "Bestehende Zuordnung (Z26) wird empfangen", "44036", None, "Z26", "mittel", True, True),
    ("LB-44036-02", "Zuordnung wird der richtigen Marktlokation zugeordnet", "44036", None, None, "mittel", True, True),
    ("LB-44037-01", "Beendigung der Zuordnung (ZC8)", "44037", None, "ZC8", "mittel", True, True),
    ("LB-44037-02", "Ende und ggf. Bilanzierungsende werden verarbeitet", "44037", None, None, "mittel", True, True),
    ("LB-44038-ZG9", "Aufhebung wegen Auszug", "44038", None, "ZG9", "mittel", True, True),
    ("LB-44038-ZH0", "Aufhebung wegen anderem Lieferant mit frueherem Termin", "44038", None, "ZH0", "mittel", True, True),
    ("LB-44038-ZH1", "Aufhebung wegen Stilllegung", "44038", None, "ZH1", "mittel", True, True),
    ("LB-44038-REFERENZ", "Urspruenglich bestaetigter Beginn wird referenziert", "44038", None, None, "mittel", True, True),
    ("LB-44038-NUR-ZUKUENFTIG", "Nur zukuenftige Zuordnung wird aufgehoben", "44038", None, None, "hoch", True, True),
    ("LB-44038-AKTIV-UNVERAENDERT", "Aktive Zuordnung bleibt unveraendert", "44038", None, None, "hoch", True, True),

    # --- PI 44022-44024: Stornierung (11) ---
    ("LB-44022-01", "Offene Anmeldung (PI 44001) wird storniert", "44022", None, None, "mittel", True, True),
    ("LB-44022-02", "Storno referenziert urspruengliche Vorgangsnummer", "44022", None, None, "mittel", True, True),
    ("LB-44022-03", "Nur der referenzierte Vorgang wird storniert", "44022", None, None, "mittel", True, True),
    ("LB-44022-04", "Urspruengliche Anmeldung wird danach nicht mehr beantwortet", "44022", None, None, "hoch", True, True),
    ("LB-44022-05", "Storno nach bereits erfolgter Antwort wird abgelehnt", "44022", None, None, "hoch", True, True),
    ("LB-44022-06", "Storno mit unbekannter Referenz", "44022", None, None, "mittel", True, True),
    ("LB-44023-01", "Bestaetigung der Stornierungsanfrage", "44023", None, None, "mittel", True, True),
    ("LB-44023-02", "Korrekte Referenz auf urspruengliche Stornierungsanfrage", "44023", None, None, "mittel", True, True),
    ("LB-44024-01", "Ablehnung der Stornierungsanfrage", "44024", None, None, "mittel", True, True),
    ("LB-44024-02", "Ablehnung Sonstiges mit Pflichtbemerkung", "44024", None, "E14", "mittel", True, True),
    ("LB-44024-03", "Parallele Anmeldungen - falscher Vorgang bleibt aktiv", "44024", None, None, "hoch", True, True),

    # --- PI 44035: Geschaeftsdaten (6) ---
    ("LB-44035-IDENT", "Erfolgreiche Identifizierung", "44035", None, None, "niedrig", True, True),
    ("LB-44035-VOLLSTAENDIG", "Vollstaendige Antwortdaten", "44035", None, None, "niedrig", True, True),
    ("LB-44035-SLP-UMFANG", "SLP-Datenumfang korrekt", "44035", None, None, "niedrig", True, False),
    ("LB-44035-RLM-UMFANG", "RLM-Datenumfang korrekt", "44035", None, None, "niedrig", False, True),
    ("LB-44035-KEIN-KORREKTUR", "Keine Verwendung als Korrekturanfrage", "44035", None, None, "mittel", True, True),
    ("LB-44035-ZUORDNUNG", "Zuordnung zur richtigen Anfrage", "44035", None, None, "mittel", True, True),

    # --- PI 44019-44021: Bestandsabgleich (7) ---
    ("LB-44019-MONATSLISTE", "Bestaetigter Lieferbeginn in richtiger Monatsliste", "44019", None, None, "mittel", True, True),
    ("LB-44019-NNBEGINN", "Netznutzungs-/Bilanzierungsbeginn entspricht Bestaetigung", "44019", None, None, "mittel", True, True),
    ("LB-44019-SLP-PROGNOSE", "SLP-Jahresverbrauchsprognose vorhanden", "44019", None, None, "niedrig", True, False),
    ("LB-44019-RLM-FALLGRUPPE", "RLM-Fallgruppe/Abrechnungsdaten korrekt", "44019", None, None, "niedrig", False, True),
    ("LB-44019-UNBEKANNT", "Unbekannte Marktlokation wird abgelehnt", "44019", None, None, "mittel", True, True),
    ("LB-44020-ABWEICHUNG", "Abweichung wird ueber Aenderungsmeldung gemeldet", "44020", None, None, "niedrig", True, True),
    ("LB-44021-ANTWORT", "Zustimmung/Ablehnung ueber Antwort auf Aenderungsmeldung", "44021", None, None, "niedrig", True, True),
]

# --- Regulatory Intelligence: Demo-Daten fuer ein reales Vorher-Nachher-Paar ---
# (Planungsdokument Abschnitt 11.8 -- feste Seed-/Demo-Daten statt Live-Monitoring.
# Mitteilung 56 ist die verbindliche Endfassung nach der Konsultation aus
# Mitteilung 55 der BNetzA-Beschlusskammer 6 (Zug/Mess/Datenformate). Kein
# automatischer Scraper/Monitoring-Job -- die Aenderungen unten sind manuell
# nachempfunden, nicht automatisch aus dem Dokument extrahiert.)
REGULATORY_VERSION_2 = {
    "name": "Mitteilung Nr. 56 / gültig ab 01.10.2026",
    "sector": "gas",
    "status": "verbindlich",
    # Stichtag als echtes Feld, nicht nur im Namen -- die Kunden-Ansicht rechnet
    # daraus den Countdown ("noch X Wochen bis zum Stichtag").
    "valid_from": datetime(2026, 10, 1),
    "source_reference": (
        "https://www.bundesnetzagentur.de/DE/Beschlusskammern/BK06/BK6_83_Zug_Mess/"
        "835_mitteilungen_datenformate/Mitteilung_56/Mitteilung_Nr_56.html"
    ),
    "is_active": False,  # bevorstehende Formatumstellung -- noch nicht der Standardkatalog
    # Kuratierte Kurzfassung fuer die Kunden-Vorschau -- manuell formuliert, nicht
    # automatisch erzeugt (im MVP gibt es keine Live-Analyse-Pipeline, Abschnitt 11.8).
    "summary": (
        "Mitteilung 56 ist die verbindliche Endfassung nach der Konsultation aus "
        "Mitteilung 55. Inhaltlich betrifft sie vor allem zwei Punkte: die neue "
        "Anwendungsübersicht der Prüfidentifikatoren (Version 4.0) und aktualisierte "
        "Codeliste-Konfigurationen (Version 1.4). Für Lieferanten heißt das: die "
        "bestehende PI-Zuordnung muss gegen die neue Übersicht abgeglichen und die "
        "Codelisten in den Umsystemen nachgezogen werden. Der Aufwand ist überschaubar, "
        "der Stichtag mit dem 01.10.2026 aber verbindlich."
    ),
}

# (title, description, category, risk, effort, effort_person_days, recommendation,
#  message_type, process_group_code, pi_number)
# process_group_code/pi_number sind optional (None), wenn die Aenderung katalogweit
# gilt statt an eine einzelne Prozessgruppe/PI gebunden zu sein.
# message_type nur setzen, wenn KEIN PI verknuepft ist -- sonst wird der Typ aus
# ProcessIdentifier.message_type abgeleitet (siehe RegulatoryChange.effective_message_type).
REGULATORY_CHANGES_V2 = [
    (
        "Neue Anwendungsübersicht der Prüfidentifikatoren 4.0",
        "Mitteilung 56 führt eine überarbeitete Anwendungsübersicht der PIs ein "
        "(Version 4.0) -- betrifft die Zuordnung von Prüfidentifikatoren über "
        "mehrere Prozessgruppen hinweg und muss gegen den bestehenden Katalog "
        "abgeglichen werden.",
        "neue_qualitaetsregel", "mittel", "mittel", 5,
        "Bestehende PI-Zuordnungen gegen die neue Übersicht 4.0 abgleichen und "
        "Abweichungen dokumentieren, bevor die Testfälle angepasst werden.",
        "UTILMD", None, None,
    ),
    (
        "Änderungen an Codeliste-Konfigurationen 1.4",
        "Codeliste-Konfigurationen wurden auf Version 1.4 aktualisiert -- "
        "einzelne Codes wurden ergänzt bzw. umbenannt. Technisch schmale, aber "
        "verbindliche Anpassung.",
        "neuer_code", "niedrig", "niedrig", 1,
        "Codelisten im Umsystem aktualisieren und die betroffenen Mappings "
        "einmalig gegen die neue Fassung prüfen.",
        "MSCONS", None, None,
    ),
    (
        "Neue Testfälle für die Anmeldung (PI 44001)",
        "Mitteilung 56 ergänzt zusätzliche Prüffälle für den Anmeldeprozess, "
        "u.a. zur Konsistenz der neuen PI-Anwendungsübersicht.",
        "neuer_testfall", "niedrig", "niedrig", 2,
        "Die ergänzten Prüffälle in den bestehenden Testkatalog für PI 44001 "
        "aufnehmen und im nächsten Regressionslauf mitfahren lassen.",
        None, "registration", "44001",  # message_type wird aus PI 44001 abgeleitet
    ),
]

# Requirement-Katalog der neuen Version: Mitteilung 56 ersetzt den bestehenden
# Katalog nicht, sondern ergaenzt ihn -- der Seed uebernimmt daher alle Requirements
# aus Version 1 unveraendert und legt zusaetzlich die unten gelisteten neuen an.
# Ohne das wuerde der Diff den leeren Katalog als "alles entfallen" lesen.
# (code, title, pi_number, transaction_reason, response_code, criticality, slp, rlm)
REQUIREMENTS_V2_NEW = [
    ("LB-44001-PI-UEBERSICHT-40", "PI-Zuordnung nach Anwendungsübersicht 4.0", "44001", None, None, "hoch", True, True),
    ("LB-44003-CODELISTE-14", "Antwortcodes gemäß Codeliste-Konfiguration 1.4", "44003", None, None, "mittel", True, True),
    ("LB-44001-TESTFALL-M56", "Ergänzte Prüffälle Anmeldung (Mitteilung 56)", "44001", None, None, "mittel", True, True),
]

DEMO_CUSTOMER_NAME = "Demo Gaslieferant GmbH"

IMPLEMENTIERT = "implementiert"
NICHT_IMPLEMENTIERT = "nicht_implementiert"
GETESTET = "getestet"
NICHT_GETESTET = "nicht_getestet"
ERFOLGREICH = "erfolgreich"
OFFEN = "offen"
VORHANDEN = "vorhanden"
FEHLT = "fehlt"
