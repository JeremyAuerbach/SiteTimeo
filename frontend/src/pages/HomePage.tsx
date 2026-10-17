import { useEffect, useState } from "react";

import type { User } from "../api";
import Avatar from "../components/Avatar";
import { AccountIcon, LogoutIcon, QuizIcon } from "../components/Icons";
import AccountTab from "./AccountTab";
import QuizTab from "./QuizTab";

const TABS = [
  { id: "quizz", label: "Quizz", Icon: QuizIcon },
  { id: "compte", label: "Compte", Icon: AccountIcon },
] as const;

type TabId = (typeof TABS)[number]["id"];

// L'onglet ouvert est gardé dans l'adresse (#quizz, #compte) : il survit au rechargement.
function tabFromHash(): TabId {
  const hash = window.location.hash.slice(1);
  return TABS.some((tab) => tab.id === hash) ? (hash as TabId) : "quizz";
}

type Props = {
  user: User;
  onUserChange: (user: User) => void;
  onLogout: () => void;
};

export default function HomePage({ user, onUserChange, onLogout }: Props) {
  const [tab, setTab] = useState<TabId>(tabFromHash);

  useEffect(() => {
    const onHashChange = () => setTab(tabFromHash());
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
              className={tab === id ? "nav-item active" : "nav-item"}
              aria-current={tab === id ? "page" : undefined}
            >
              <Icon />
              <span>{label}</span>
            </a>
          ))}
        </nav>

        <div className="sidebar-user">
          <Avatar user={user} size={36} />
          <div className="sidebar-user-text">
            <span className="sidebar-username">{user.username}</span>
            <span className="sidebar-role">{user.is_guest ? "Visiteur" : "Compte"}</span>
          </div>
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
        {tab === "quizz" ? (
          <QuizTab user={user} />
        ) : (
          <AccountTab user={user} onUserChange={onUserChange} />
        )}
      </main>
    </div>
  );
}
