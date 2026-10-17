import { type ChangeEvent, type FormEvent, type ReactNode, useRef, useState } from "react";

import { api, type User } from "../api";
import Avatar from "../components/Avatar";
import { prepareAvatar } from "../image";

type Props = { user: User; onUserChange: (user: User) => void };

export default function AccountTab({ user, onUserChange }: Props) {
  return (
    <div className="tab-page">
      <header className="tab-header">
        <div>
          <h1>Compte</h1>
          <p className="hint">
            {user.is_guest
              ? "Compte visiteur : il sera supprimé quand tu quitteras l'application."
              : "Ta photo, ton pseudo et ton mot de passe."}
          </p>
        </div>
      </header>

      <AvatarSection user={user} onUserChange={onUserChange} />
      <UsernameSection user={user} onUserChange={onUserChange} />
      <PasswordSection user={user} />
    </div>
  );
}

/** Suivi de l'envoi d'un formulaire : en cours, erreur, ou message de réussite. */
function useAction() {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState<string | null>(null);

  async function run(action: () => Promise<string>) {
    setPending(true);
    setError(null);
    setDone(null);
    try {
      setDone(await action());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Une erreur est survenue.");
    } finally {
      setPending(false);
    }
  }

  return { pending, error, done, run };
}

function Feedback({ error, done }: { error: string | null; done: string | null }) {
  if (error)
    return (
      <p className="error" role="alert">
        {error}
      </p>
    );
  if (done)
    return (
      <p className="success" role="status">
        {done}
      </p>
    );
  return null;
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="panel">
      <h2>{title}</h2>
      {children}
    </section>
  );
}

function AvatarSection({ user, onUserChange }: Props) {
  const input = useRef<HTMLInputElement>(null);
  const { pending, error, done, run } = useAction();

  function onFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    run(async () => {
      onUserChange(await api.uploadAvatar(await prepareAvatar(file)));
      return "Photo mise à jour.";
    });
  }

  function remove() {
    run(async () => {
      onUserChange(await api.deleteAvatar());
      return "Photo retirée.";
    });
  }

  return (
    <Section title="Photo de profil">
      <div className="avatar-row">
        <Avatar user={user} size={88} />
        <div className="avatar-actions">
          <input
            ref={input}
            id="avatar-file"
            type="file"
            accept="image/png,image/jpeg,image/webp,image/gif"
            onChange={onFile}
            hidden
          />
          <button
            type="button"
            className="primary"
            onClick={() => input.current?.click()}
            disabled={pending}
          >
            {user.avatar_url ? "Changer la photo" : "Ajouter une photo"}
          </button>
          {user.avatar_url && (
            <button type="button" className="secondary" onClick={remove} disabled={pending}>
              Retirer
            </button>
          )}
        </div>
      </div>
      <p className="hint small">PNG, JPEG, WebP ou GIF. L'image est recadrée au carré.</p>
      <Feedback error={error} done={done} />
    </Section>
  );
}

function UsernameSection({ user, onUserChange }: Props) {
  const [username, setUsername] = useState(user.username);
  const { pending, error, done, run } = useAction();

  function submit(event: FormEvent) {
    event.preventDefault();
    run(async () => {
      const updated = await api.updateUsername(username);
      onUserChange(updated);
      setUsername(updated.username);
      return "Pseudo modifié.";
    });
  }

  return (
    <Section title="Pseudo">
      <form className="form" onSubmit={submit}>
        <label>
          Nouveau pseudo
          <input
            id="account-username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            required
          />
        </label>
        <Feedback error={error} done={done} />
        <div className="form-actions">
          <button
            type="submit"
            className="primary"
            disabled={pending || username.trim() === user.username}
          >
            Enregistrer
          </button>
        </div>
      </form>
    </Section>
  );
}

function PasswordSection({ user }: { user: User }) {
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");
  const { pending, error, done, run } = useAction();

  if (user.is_guest) {
    return (
      <Section title="Mot de passe">
        <p className="hint">Un compte visiteur n'a pas de mot de passe.</p>
      </Section>
    );
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    run(async () => {
      if (next !== confirm) throw new Error("Les deux nouveaux mots de passe ne correspondent pas.");
      await api.updatePassword(current, next);
      setCurrent("");
      setNext("");
      setConfirm("");
      return "Mot de passe modifié. Tes autres appareils ont été déconnectés.";
    });
  }

  return (
    <Section title="Mot de passe">
      <form className="form" onSubmit={submit}>
        {/* Aide les gestionnaires de mots de passe à savoir de quel compte il s'agit. */}
        <input type="text" value={user.username} autoComplete="username" readOnly hidden />
        <label>
          Mot de passe actuel
          <input
            id="password-current"
            type="password"
            value={current}
            onChange={(e) => setCurrent(e.target.value)}
            autoComplete="current-password"
            required
          />
        </label>
        <label>
          Nouveau mot de passe
          <input
            id="password-new"
            type="password"
            value={next}
            onChange={(e) => setNext(e.target.value)}
            autoComplete="new-password"
            minLength={8}
            required
          />
        </label>
        <label>
          Confirmer le nouveau mot de passe
          <input
            id="password-confirm"
            type="password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            autoComplete="new-password"
            minLength={8}
            required
          />
        </label>
        <Feedback error={error} done={done} />
        <div className="form-actions">
          <button type="submit" className="primary" disabled={pending}>
            Changer le mot de passe
          </button>
        </div>
      </form>
    </Section>
  );
}
