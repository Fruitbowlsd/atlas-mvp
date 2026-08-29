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
// Die drei Unternehmen sind frei erfunden; Aufbau, Masse und SVGs stammen aus
// Atlas_Login_Preview.html im Projektordner. Die SVGs sind dort auf viewBox
// 0 0 36 36 neu gezeichnet -- nicht die alten 52er skaliert.
function LogoSet() {
  return (
    <>
      {/* Stadtwerke Nordlicht */}
      <div className="logo-item">
        <div className="logo-icon" style={{ background: "#003366" }}>
          <svg width="36" height="36" viewBox="0 0 36 36" aria-hidden="true">
            <text x="18" y="24" textAnchor="middle" fontSize="14" fontWeight="700" fill="white" fontFamily="Arial">N</text>
            <polygon points="22,6 17,18 21,18 15,30 26,15 21,15" fill="#00AAFF" opacity="0.9" />
          </svg>
        </div>
        <div className="logo-text">
          <div className="logo-name" style={{ color: "#003366" }}>Stadtwerke<br />Nordlicht</div>
          <div className="logo-tagline">Energie · Wärme · Wasser</div>
        </div>
      </div>

      {/* EnerTec */}
      <div className="logo-item">
        <div className="logo-icon" style={{ background: "#1a8a3c" }}>
          <svg width="36" height="36" viewBox="0 0 36 36" aria-hidden="true">
            <text x="18" y="25" textAnchor="middle" fontSize="20" fontWeight="900" fill="white" fontFamily="Arial">E</text>
            <rect x="6" y="30" width="24" height="2" rx="1" fill="#7fdc9f" />
          </svg>
        </div>
        <div className="logo-text">
          <div className="logo-name">
            <span style={{ color: "#1a8a3c" }}>Ener</span>
            <span style={{ color: "#333" }}>Tec</span>
          </div>
          <div className="logo-tagline">Regional · Digital · Grün</div>
        </div>
      </div>

      {/* Rheingas & Wärme */}
      <div className="logo-item">
        <div className="logo-icon" style={{ background: "#c0392b" }}>
          <svg width="36" height="36" viewBox="0 0 36 36" aria-hidden="true">
            <path d="M18 4 C11 13 9 20 13 26 C14 22 16 20 18 22 C20 20 22 22 23 26 C27 20 25 13 18 4Z" fill="white" opacity="0.95" />
            <ellipse cx="18" cy="25" rx="5" ry="6" fill="#f39c12" opacity="0.85" />
          </svg>
        </div>
        <div className="logo-text">
          <div className="logo-name">
            <span style={{ color: "#c0392b" }}>Rheingas</span>
            <br />
            <span style={{ color: "#555" }}>&amp; Wärme</span>
          </div>
          <div className="logo-tagline">Seit 1952 · Verlässlich</div>
        </div>
      </div>
    </>
  );
}

function ReferencePanel() {
  return (
    <aside className="login-reference">
      {/* Bewusst ohne "in Deutschland": das vollstaendige Label fuellte die 320px
          fast allein, die Trennstriche links und rechts blieben 6px kurz.
          So bleiben je 50px Strich und die Zeile wirkt als Trennlinie. */}
      <div className="login-reference-heading">Vertraut von führenden EVUs</div>

      <div className="ticker-outer">
        <div className="ticker-track">
          <LogoSet />
          {/* Zweite, identische Reihe: nach genau einer Reihenbreite steht die
              Kopie dort, wo das Original stand -- der Ruecksprung ist dadurch
              unsichtbar. Fuer Screenreader ist sie eine Dublette. */}
          <div className="ticker-copy" aria-hidden="true">
            <LogoSet />
          </div>
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
