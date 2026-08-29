import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import type { EmailCheckResult } from "../types";

/** Zweistufiger Login (Abschnitt 13.4): erst die E-Mail, dann das Passwort.
 *
 *  Die Domain wird bereits beim Tippen geprueft. Ist fuer sie SSO hinterlegt,
 *  erscheint der Microsoft-Button ZUSAETZLICH zum Passwort-Weg -- der Nutzer muss
 *  also nicht erst abschicken, um zu erfahren, wie er sich anmelden kann. */

const CHECK_DEBOUNCE_MS = 500;

/** Erst pruefen, wenn ueberhaupt eine Domain dasteht. Ohne diese Bremse loeste jeder
 *  Tastendruck eine Anfrage aus, die noch gar nichts entscheiden kann. */
function hasDomain(email: string): boolean {
  const domain = email.split("@")[1];
  return Boolean(domain && domain.includes("."));
}

// TODO: Echte Kundenlogos und Zitate einsetzen, sobald Pilotkunden
// ihr Einverständnis gegeben haben. Fiktive Logos bis dahin.
//
// Die drei Unternehmen sind frei erfunden; die SVG-Strukturen stammen aus
// Atlas_Beispiellogos.html im Projektordner und sind unveraendert uebernommen.
function ReferencePanel() {
  return (
    <aside className="login-reference">
      <p className="login-reference-heading">Vertraut von führenden EVUs in Deutschland</p>

      <div className="login-logos">
        {/* Stadtwerke Nordlicht */}
        <div className="ref-logo">
          <div className="ref-logo-icon" style={{ background: "#003366" }}>
            <svg viewBox="0 0 52 52" aria-hidden="true">
              <text x="26" y="34" textAnchor="middle" fontSize="20" fontWeight="700" fill="white" fontFamily="Arial">N</text>
              <polygon points="32,8 24,26 30,26 22,44 38,22 30,22" fill="#00AAFF" opacity="0.9" />
            </svg>
          </div>
          <span className="ref-logo-name" style={{ color: "#003366" }}>Stadtwerke Nordlicht</span>
          <span className="ref-logo-tagline">Energie · Wärme · Wasser</span>
        </div>

        {/* EnerTec */}
        <div className="ref-logo">
          <div className="ref-logo-icon" style={{ background: "#1a8a3c" }}>
            <svg viewBox="0 0 52 52" aria-hidden="true">
              <text x="26" y="36" textAnchor="middle" fontSize="28" fontWeight="900" fill="white" fontFamily="Arial">E</text>
              <rect x="8" y="44" width="36" height="3" rx="1.5" fill="#7fdc9f" />
            </svg>
          </div>
          <span className="ref-logo-name">
            <span style={{ color: "#1a8a3c" }}>Ener</span>
            <span style={{ color: "#333" }}>Tec</span>
          </span>
          <span className="ref-logo-tagline">Regional · Digital · Grün</span>
        </div>

        {/* Rheingas & Wärme */}
        <div className="ref-logo">
          <div className="ref-logo-icon" style={{ background: "#c0392b" }}>
            <svg viewBox="0 0 52 52" aria-hidden="true">
              <path d="M26 6 C16 18 13 28 18 37 C20 32 22 30 26 32 C30 30 32 32 34 37 C39 28 36 18 26 6Z" fill="white" opacity="0.95" />
              <ellipse cx="26" cy="35" rx="7" ry="9" fill="#f39c12" opacity="0.8" />
            </svg>
          </div>
          <span className="ref-logo-name" style={{ color: "#c0392b" }}>
            Rheingas <span style={{ color: "#555" }}>&amp; Wärme</span>
          </span>
          <span className="ref-logo-tagline">Seit 1952 · Verlässlich</span>
        </div>
      </div>

      <p className="login-reference-disclaimer">
        * Fiktive Beispiele – Ihre Organisation könnte hier stehen.
      </p>
    </aside>
  );
}

export function Login({ onSuccess }: { onSuccess: () => void }) {
  const [email, setEmail] = useState("");
  const [check, setCheck] = useState<EmailCheckResult | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Beim Tippen koennen mehrere Anfragen gleichzeitig unterwegs sein und in
  // beliebiger Reihenfolge zurueckkommen. Nur die Antwort zur zuletzt getippten
  // Adresse darf zaehlen, sonst blinkt der SSO-Button eines aelteren Standes auf.
  const latestCheck = useRef(0);

  useEffect(() => {
    const value = email.trim().toLowerCase();
    const seq = ++latestCheck.current;
    setCheck(null);

    if (!hasDomain(value)) return;

    const timer = setTimeout(async () => {
      try {
        const result = await api.checkEmail(value);
        if (seq === latestCheck.current) setCheck(result);
      } catch {
        // Die Live-Pruefung ist eine Zugabe. Schlaegt sie fehl, bleibt der
        // Passwort-Weg unveraendert nutzbar -- deshalb hier bewusst keine
        // Fehlermeldung, die den Nutzer vom Anmelden abhaelt.
      }
    }, CHECK_DEBOUNCE_MS);

    return () => clearTimeout(timer);
  }, [email]);

  const handleContinueWithEmail = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) {
      setError("Bitte eine E-Mail-Adresse eingeben.");
      return;
    }
    setError(null);
    setShowPassword(true);
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await api.login(email.trim(), password);
      onSuccess();
    } catch {
      setError("E-Mail oder Passwort ist falsch.");
    } finally {
      setSubmitting(false);
    }
  };

  const back = () => {
    setShowPassword(false);
    setPassword("");
    setError(null);
  };

  // Steht in beiden Schritten zur Verfuegung: wer den Passwort-Weg eingeschlagen
  // hat, aber ein SSO-Konto besitzt, landet sonst in einer Sackgasse.
  const ssoOption = (
    <>
      {check?.mode === "sso" && (
        // Bewusst ein Link, kein fetch: der OIDC-Ablauf ist ein Seitenwechsel
        // zum Anbieter und zurueck.
        <a className="recalc-button login-button login-button-secondary" href="/auth/login">
          Mit Microsoft anmelden
        </a>
      )}
      {check?.mode === "sso_unavailable" && (
        <div className="form-error" style={{ marginTop: 14 }}>
          Für diese Organisation ist die Anmeldung über Microsoft vorgesehen,
          aber noch nicht fertig eingerichtet. Bitte an den Atlas-Support wenden.
        </div>
      )}
    </>
  );

  return (
    <div className="login-page">
      <div className="login-layout">
        <div className="login-card">
          <div className="brand" style={{ marginBottom: 6, justifyContent: "center" }}>
            <div className="brand-mark">A</div>
            <div>
              <div className="brand-name">Atlas</div>
              <div className="brand-sub">Energy Quality Assessment</div>
            </div>
          </div>

          {!showPassword ? (
            <>
              <form onSubmit={handleContinueWithEmail}>
                <p className="login-hint">Bitte mit der geschäftlichen E-Mail-Adresse anmelden.</p>
                <input
                  type="email"
                  className="text-input"
                  placeholder="name@unternehmen.de"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoFocus
                />
                {error && <div className="form-error" style={{ marginTop: 12 }}>{error}</div>}
                <button type="submit" className="recalc-button login-button">
                  Weiter
                </button>
              </form>
              {ssoOption}
            </>
          ) : (
            <>
              <p className="login-hint">
                <strong>{email}</strong>
              </p>

              <form onSubmit={handlePasswordSubmit}>
                <input
                  type="password"
                  className="text-input"
                  placeholder="Passwort"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoFocus
                />
                {error && <div className="form-error" style={{ marginTop: 12 }}>{error}</div>}
                <button type="submit" className="recalc-button login-button" disabled={submitting}>
                  {submitting ? "Prüfe …" : "Anmelden"}
                </button>
              </form>

              {ssoOption}

              <button type="button" className="link-button login-back" onClick={back}>
                Andere E-Mail-Adresse verwenden
              </button>
            </>
          )}
        </div>
        <ReferencePanel />
      </div>
    </div>
  );
}
