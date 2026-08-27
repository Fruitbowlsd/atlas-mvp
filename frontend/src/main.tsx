import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { AdminApp } from "./admin/AdminApp";
import "./index.css";

// Bewusst ein Pfad-Abgleich statt einer Router-Bibliothek: die Kunden-App navigiert
// bereits ueber State, ein Router waere hier ein Umbau ohne Mehrwert. Der Server
// liefert fuer /admin dieselbe index.html aus (SPA-Fallback in main.py).
const isAdmin = window.location.pathname.startsWith("/admin");

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    {isAdmin ? <AdminApp /> : <App />}
  </React.StrictMode>
);
