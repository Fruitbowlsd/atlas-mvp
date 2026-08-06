import { useState } from "react";
import { api } from "../api/client";

export function Login({ onSuccess }: { onSuccess: () => void }) {
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await api.login(password);
      onSuccess();
    } catch {
      setError("Falsches Passwort.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={handleSubmit}>
        <div className="brand" style={{ marginBottom: 6, justifyContent: "center" }}>
          <div className="brand-mark">A</div>
          <div>
            <div className="brand-name">Atlas</div>
            <div className="brand-sub">Energy Quality Assessment</div>
          </div>
        </div>
        <p style={{ color: "var(--text-muted)", fontSize: 13, textAlign: "center", margin: "0 0 22px" }}>
          Diese Demo ist passwortgeschützt.
        </p>
        <input
          type="password"
          className="text-input"
          placeholder="Passwort"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoFocus
        />
        {error && <div className="form-error" style={{ marginTop: 12 }}>{error}</div>}
        <button type="submit" className="recalc-button" disabled={submitting} style={{ width: "100%", marginTop: 14 }}>
          {submitting ? "Prüfe …" : "Anmelden"}
        </button>
      </form>
    </div>
  );
}
