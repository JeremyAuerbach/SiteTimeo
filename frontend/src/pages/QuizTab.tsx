import { type FormEvent, useState } from "react";

import type { User } from "../api";
import { EXAMPLE_QUIZZES, type Quiz, QUIZ_THEMES, STATUS_LABELS } from "../quiz/exemples";

export default function QuizTab({ user }: { user: User }) {
  const [quizzes, setQuizzes] = useState<Quiz[]>(EXAMPLE_QUIZZES);
  const [creating, setCreating] = useState(false);

  function addQuiz(quiz: Omit<Quiz, "id" | "host" | "players" | "status">) {
    setQuizzes((list) => [
      { ...quiz, id: Date.now(), host: user.username, players: 0, status: "preparation" },
      ...list,
    ]);
    setCreating(false);
  }

  return (
    <div className="tab-page">
      <header className="tab-header">
        <div>
          <h1>Quizz</h1>
          <p className="hint">Les quizz qui se déroulent en ce moment ou vont bientôt commencer.</p>
        </div>
        {!creating && (
          <button type="button" className="primary" onClick={() => setCreating(true)}>
            Créer un quizz
          </button>
        )}
      </header>

      <p className="preview-note">
        Aperçu : les quizz ci-dessous sont des exemples et ceux que tu crées ne sont pas encore
        enregistrés.
      </p>

      {creating && <CreateQuizForm onCreate={addQuiz} onCancel={() => setCreating(false)} />}

      <ul className="quiz-list">
        {quizzes.map((quiz) => (
          <li key={quiz.id} className="quiz-card">
            <div className="quiz-main">
              <span className={`status status-${quiz.status}`}>{STATUS_LABELS[quiz.status]}</span>
              <h2>{quiz.title}</h2>
              <p className="quiz-meta">
                {quiz.theme} · {quiz.questionCount} questions · animé par {quiz.host}
              </p>
            </div>
            <div className="quiz-side">
              <span className="quiz-players">
                {quiz.players} joueur{quiz.players > 1 ? "s" : ""}
              </span>
              <button type="button" className="secondary" disabled title="Bientôt disponible">
                {quiz.host === user.username ? "Ouvrir" : "Rejoindre"}
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

type FormProps = {
  onCreate: (quiz: { title: string; theme: string; questionCount: number }) => void;
  onCancel: () => void;
};

function CreateQuizForm({ onCreate, onCancel }: FormProps) {
  const [title, setTitle] = useState("");
  const [theme, setTheme] = useState(QUIZ_THEMES[0]);
  const [questionCount, setQuestionCount] = useState(10);

  function submit(event: FormEvent) {
    event.preventDefault();
    onCreate({ title: title.trim(), theme, questionCount });
  }

  return (
    <form className="panel form" onSubmit={submit}>
      <h2>Nouveau quizz</h2>
      <label>
        Titre
        <input
          id="quiz-title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          maxLength={80}
          placeholder="Ex. Capitales d'Asie"
          required
          autoFocus
        />
      </label>
      <div className="form-row">
        <label>
          Thème
          <select id="quiz-theme" value={theme} onChange={(e) => setTheme(e.target.value)}>
            {QUIZ_THEMES.map((t) => (
              <option key={t}>{t}</option>
            ))}
          </select>
        </label>
        <label>
          Nombre de questions
          <input
            id="quiz-questions"
            type="number"
            min={1}
            max={50}
            value={questionCount}
            onChange={(e) => setQuestionCount(Number(e.target.value))}
            required
          />
        </label>
      </div>
      <div className="form-actions">
        <button type="button" className="secondary" onClick={onCancel}>
          Annuler
        </button>
        <button type="submit" className="primary">
          Créer le quizz
        </button>
      </div>
    </form>
  );
}
