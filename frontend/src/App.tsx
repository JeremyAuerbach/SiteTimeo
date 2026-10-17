import { useEffect, useState } from "react";

import { api, ApiError, type User } from "./api";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";

// Un visiteur doit donner signe de vie régulièrement : sans activité, le serveur
// considère qu'il a quitté l'application et supprime son compte temporaire.
const GUEST_HEARTBEAT_MS = 60_000;

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .me()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!user?.is_guest) return;
    const timer = setInterval(() => {
      api.me().catch((error) => {
        if (error instanceof ApiError && error.status === 401) setUser(null);
      });
    }, GUEST_HEARTBEAT_MS);
    return () => clearInterval(timer);
  }, [user]);

  async function logout() {
    await api.logout().catch(() => undefined);
    setUser(null);
  }

  if (loading) return <main className="screen" aria-busy="true" />;
  return user ? <HomePage user={user} onUserChange={setUser} onLogout={logout} /> : <LoginPage onLogin={setUser} />;
}
