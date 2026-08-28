import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      // Der OIDC-Ablauf laeuft ausserhalb von /api, weil er ein Seitenwechsel im
      // Browser ist. Ohne diesen Eintrag liefe der SSO-Button lokal gegen den
      // Vite-Server statt gegen das Backend.
      "/auth": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
