/** Versionsbezeichnungen tragen den Stichtag haeufig schon im Namen
 *  ("GeLi Gas 2.0 / UTILMD Gas G1.1 (gültig ab 01.04.2026)"). Ein zusaetzlich
 *  ausgegebenes "gültig ab …" waere dann eine sichtbare Doppelung. Diese Funktion
 *  liefert das Datum nur, wenn es im Namen noch nicht vorkommt -- an einer Stelle,
 *  damit die Regel nicht in mehreren Komponenten auseinanderlaeuft. */
export function redundantFreeValidFrom(name: string | null, validFrom: string | null): string | null {
  if (!validFrom) return null;
  const date = new Date(validFrom);
  if (Number.isNaN(date.getTime())) return null;

  const formatted = date.toLocaleDateString("de-DE");
  if (!name) return formatted;

  // Sowohl "1.10.2026" als auch "01.10.2026" abdecken -- beide Schreibweisen
  // kommen in gepflegten Bezeichnungen vor.
  const variants = [
    formatted,
    date.toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit", year: "numeric" }),
  ];
  return variants.some((v) => name.includes(v)) ? null : formatted;
}

/** Gueltigkeit in Worten. "gültig ab 01.04.2026" liest sich schief, sobald der
 *  Stichtag vorbei ist -- dann ist die Version schlicht die zurzeit geltende. */
export function validityLabel(name: string | null, validFrom: string | null): string | null {
  if (!validFrom) return null;
  const date = new Date(validFrom);
  if (Number.isNaN(date.getTime())) return null;

  // Datum nur nennen, wenn es nicht schon in der Bezeichnung steht.
  const dateText = redundantFreeValidFrom(name, validFrom);
  const alreadyInForce = date <= new Date();

  if (alreadyInForce) {
    return dateText ? `Zurzeit gültige Version (seit ${dateText})` : "Zurzeit gültige Version";
  }
  return dateText ? `Künftige Version · gültig ab ${dateText}` : "Künftige Version";
}
