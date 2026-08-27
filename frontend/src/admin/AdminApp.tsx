import { useCallback, useEffect, useState } from "react";
import { api } from "../api/client";
import type { CurrentUser } from "../types";
import { Login } from "../components/Login";
import { RegulatoryChanges } from "../components/RegulatoryChanges";
import { AdminTenants } from "./AdminTenants";
import { AdminUsers } from "./AdminUsers";
import { AdminAssessments } from "./AdminAssessments";
import { AdminSystem } from "./AdminSystem";

export type AdminSection = "organisationen" | "nutzer" | "assessments" | "regulatorisch" | "system";

const SECTIONS: { key: AdminSection; label: string }[] = [
  { key: "organisationen", label: "Organisationen" },
  { key: "nutzer", label: "Nutzer" },
  { key: "assessments", label: "Assessments" },
  { key: "regulatorisch", label: "Regulatorische Stände" },
  { key: "system", label: "System" },
];

/** Eigenständige Verwaltungsoberfläche unter /admin (Issue #13) -- eigenes Layout,
 *  eigene Navigation, komplett getrennt von der Kunden-App. */
export function AdminApp() {
  const [authChecked, setAuthChecked] = useState(false);
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [section, setSection] = useState<AdminSection>("organisationen");

  const loadCurrentUser = useCallback(async () => {
    try {
      setCurrentUser(await api.me());
    } catch {
      setCurrentUser({ authenticated: false });
    } finally {
      setAuthChecked(true);
    }
  }, []);

  useEffect(() => {
    loadCurrentUser();
  }, [loadCurrentUser]);

  const handleLogout = async () => {
    try {
      const res = await api.logout();
      if (res.sso_logout_url) {
        window.location.href = res.sso_logout_url;
        return;
      }
    } catch {
      /* auch bei Fehler lokal abmelden -- der Cookie kann serverseitig abgelaufen sein */
    }
    window.location.reload();
  };

  if (!authChecked) return <div className="loading">Lade …</div>;
  if (!currentUser?.authenticated) return <Login onSuccess={loadCurrentUser} />;

  // Ohne Admin-Rechte gar nicht erst das Verwaltungs-Layout aufbauen: sonst saehe
  // ein Tenant-Nutzer die komplette Navigation samt Fehlermeldung.
  if (!currentUser.is_atlas_admin) {
    return (
      <div className="login-page">
        <div className="login-card">
          <div className="section-title" style={{ marginTop: 0 }}>Kein Zugriff</div>
          <p className="login-hint">Dieser Bereich ist dem Atlas-Team vorbehalten.</p>
          <a href="/" className="recalc-button login-button">Zur Atlas-App</a>
        </div>
      </div>
    );
  }

  return (
    <div className="app-shell admin-shell">
      <div className="sidebar admin-sidebar">
        <div className="sidebar-brand">
          <div className="brand-mark admin-mark">A</div>
          <div>
            <div className="sidebar-brand-name">Atlas</div>
            <div className="sidebar-brand-sub">Verwaltung</div>
          </div>
        </div>

        <nav className="sidebar-nav">
          {SECTIONS.map((s) => (
            <button
              key={s.key}
              className={`sidebar-item ${section === s.key ? "active" : ""}`}
              onClick={() => setSection(s.key)}
            >
              {s.label}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer" style={{ marginTop: "auto" }}>
          <div className="sidebar-footer-title">Kundenansicht</div>
          <div className="sidebar-footer-text">
            <a href="/" className="admin-back-link">← Zur Kunden-App</a>
          </div>
        </div>

        <div className="sidebar-user">
          <div className="sidebar-user-email" title={currentUser.email}>{currentUser.email}</div>
          <button className="sidebar-logout" onClick={handleLogout}>Abmelden</button>
        </div>
      </div>

      <div className="app-content admin-content">
        {section === "organisationen" && <AdminTenants />}
        {section === "nutzer" && <AdminUsers />}
        {section === "assessments" && <AdminAssessments />}
        {/* Umzug ohne funktionalen Umbau: dieselbe Komponente wie zuvor in der
            Kunden-Sidebar. Die Kunden-Vorschau braucht dort ein Assessment, das es
            im Admin-Kontext nicht gibt -- daher null. */}
        {section === "regulatorisch" && <RegulatoryChanges assessmentId={null} />}
        {section === "system" && <AdminSystem />}
      </div>
    </div>
  );
}
