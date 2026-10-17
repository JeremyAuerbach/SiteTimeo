import { useEffect, useState } from "react";

import type { User } from "../api";
import Avatar from "../components/Avatar";
import { LogoutIcon, QuizIcon } from "../components/Icons";
import AccountTab from "./AccountTab";
import QuizTab from "./QuizTab";

const TABS = [{ id: "quizz", label: "Quizz", Icon: QuizIcon }] as const;

// La page Compte n'est pas un onglet : on l'ouvre depuis le profil en bas du menu.
type View = (typeof TABS)[number]["id"] | "compte";

// La vue ouverte est gardée dans l'adresse (#quizz, #compte) : elle survit au rechargement.
function viewFromHash(): View {
  const hash = window.location.hash.slice(1);
  return hash === "compte" || TABS.some((tab) => tab.id === hash) ? (hash as View) : "quizz";
}

type Props = {
  user: User;
  onUserChange: (user: User) => void;
  onLogout: () => void;
};

export default function HomePage({ user, onUserChange, onLogout }: Props) {
  const [view, setView] = useState<View>(viewFromHash);

  useEffect(() => {
    const onHashChange = () => setView(viewFromHash());
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  return (
    <div className="shell">
      <aside className="sidebar">
        <span className="sidebar-brand">Timeo</span>

        <nav className="sidebar-nav" aria-label="Navigation principale">
          {TABS.map(({ id, label, Icon }) => (
            <a
              key={id}
              href={`#${id}`}
              className={view === id ? "nav-item active" : "nav-item"}
              aria-current={view === id ? "page" : undefined}
            >
              <Icon />
              <span>{label}</span>
            </a>
          ))}
        </nav>

        <div className="sidebar-user">
          <a
            href="#compte"
            className={view === "compte" ? "sidebar-profile active" : "sidebar-profile"}
            aria-current={view === "compte" ? "page" : undefined}
            title="Mon compte"
          >
            <Avatar user={user} size={36} />
            <span className="sidebar-user-text">
              <span className="sidebar-username">{user.username}</span>
              <span className="sidebar-role">{user.is_guest ? "Visiteur" : "Compte"}</span>
            </span>
          </a>
          <button
            type="button"
            className="icon-button"
            onClick={onLogout}
            title="Se déconnecter"
            aria-label="Se déconnecter"
          >
            <LogoutIcon />
          </button>
        </div>
      </aside>

      <main className="content">
        {view === "quizz" ? (
          <QuizTab user={user} />
        ) : (
          <AccountTab user={user} onUserChange={onUserChange} />
        )}
      </main>
    </div>
  );
}
