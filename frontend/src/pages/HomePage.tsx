import type { User } from "../api";

export default function HomePage({ user, onLogout }: { user: User; onLogout: () => void }) {
  return (
    <main className="screen">
      <section className="card">
        <p className="success">Connexion réussie</p>
        <h1>Bienvenue, {user.username} !</h1>
        <p className="hint">
          {user.is_guest
            ? "Tu es connecté en visiteur. Ce compte sera supprimé quand tu quitteras l'application."
            : "Tu es connecté à ton compte."}
        </p>
        <button type="button" className="secondary" onClick={onLogout}>
          Se déconnecter
        </button>
      </section>
    </main>
  );
}
