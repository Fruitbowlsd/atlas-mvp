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
    </div>
  );
}
