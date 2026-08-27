import { useState } from "react";
import { api } from "../api/client";
import type { EmailCheckResult } from "../types";

/** Zweistufiger Login (Abschnitt 13.4): erst die E-Mail, danach -- abhaengig von der
 *  Domain -- entweder Weiterleitung zum SSO-Anbieter oder das Passwort-Feld. */
export function Login({ onSuccess }: { onSuccess: () => void }) {
  const [email, setEmail] = useState("");
  const [check, setCheck] = useState<EmailCheckResult | null>(null);
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) {
      setError("Bitte eine E-Mail-Adresse eingeben.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      setCheck(await api.checkEmail(email.trim()));
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
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
    setCheck(null);
    setPassword("");
    setError(null);
  };

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

        {check === null ? (
          <form onSubmit={handleEmailSubmit}>
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
            <button type="submit" className="recalc-button login-button" disabled={submitting}>
              {submitting ? "Prüfe …" : "Weiter"}
            </button>
          </form>
        ) : (
          <>
            <p className="login-hint">
              <strong>{email}</strong>
            </p>

            {check.mode === "sso" && (
              <>
                <p className="login-hint">
                  Für {check.tenant_name ?? "diese Organisation"} ist die Anmeldung über
                  Microsoft eingerichtet.
                </p>
                {/* Bewusst ein Link, kein fetch: der OIDC-Ablauf ist ein
                    Seitenwechsel zum Anbieter und zurueck. */}
                <a className="recalc-button login-button" href="/auth/login">
                  Mit Microsoft anmelden
                </a>
              </>
            )}

            {check.mode === "sso_unavailable" && (
              <div className="form-error">
                Für diese Organisation ist die Anmeldung über Microsoft vorgesehen,
                aber noch nicht fertig eingerichtet. Bitte an den Atlas-Support wenden.
              </div>
            )}

            {check.mode === "password" && (
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
            )}

            <button type="button" className="link-button login-back" onClick={back}>
              Andere E-Mail-Adresse verwenden
            </button>
          </>
        )}
      </div>
    </div>
  );
}
