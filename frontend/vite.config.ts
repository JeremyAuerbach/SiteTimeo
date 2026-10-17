import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// En développement, /api est relayé vers le backend : même origine, donc les cookies passent.
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      "/api": process.env.VITE_API_PROXY ?? "http://localhost:8000",
    },
  },
});
