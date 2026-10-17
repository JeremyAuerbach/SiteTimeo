import { type FormEvent, useState } from "react";

import { api, type User } from "../api";

type Mode = "login" | "register" | "guest";

const TITLES: Record<Mode, string> = {
  login: "Se connecter",
  register: "Créer un compte",
  guest: "Entrer en visiteur",
};

export default function LoginPage({ onLogin }: { onLogin: (user: User) => void }) {
  const [mode, setMode] = useState<Mode>("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function switchMode(next: Mode) {
    setMode(next);
    setError(null);
    setPassword("");
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const user =
        mode === "login"
          ? await api.login(username, password)
          : mode === "register"
            ? await api.register(username, password)
            : await api.guest(username);
      onLogin(user);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Une erreur est survenue.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="screen">
      <section className="card">
        <h1 className="brand">Timeo</h1>

        {mode !== "guest" && (
          <div className="tabs" role="tablist">
            {(["login", "register"] as const).map((tab) => (
              <button
                key={tab}
                type="button"
                role="tab"
                aria-selected={mode === tab}
                className={mode === tab ? "tab active" : "tab"}
                onClick={() => switchMode(tab)}
              >
                {TITLES[tab]}
              </button>
            ))}
          </div>
        )}

        {mode === "guest" && (
          <>
            <h2>{TITLES.guest}</h2>
            <p className="hint">
              Choisis un pseudo. Ton compte visiteur est temporaire : il sera supprimé quand tu
              quitteras l'application.
            </p>
          </>
        )}

        <form onSubmit={submit} className="form">
          <label>
            Pseudo
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              required
              autoFocus
            />
          </label>

          {mode !== "guest" && (
            <label>
              Mot de passe
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete={mode === "login" ? "current-password" : "new-password"}
                minLength={mode === "register" ? 8 : undefined}
                required
              />
            </label>
          )}

          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}

          <button type="submit" className="primary" disabled={submitting}>
            {submitting ? "Patiente…" : TITLES[mode]}
          </button>
        </form>

        <div className="divider">
          <span>ou</span>
        </div>

        {mode === "guest" ? (
          <button type="button" className="secondary" onClick={() => switchMode("login")}>
            J'ai un compte
          </button>
        ) : (
          <button type="button" className="secondary" onClick={() => switchMode("guest")}>
            Continuer en tant que visiteur
          </button>
        )}
      </section>
    </main>
  );
}
