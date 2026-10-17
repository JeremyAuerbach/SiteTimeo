// Données d'exemple : les quizz ne sont pas encore gérés par le backend.

export type QuizStatus = "en-cours" | "bientot" | "preparation";

export type Quiz = {
  id: number;
  title: string;
  theme: string;
  host: string;
  questionCount: number;
  players: number;
  status: QuizStatus;
};

export const QUIZ_THEMES = [
  "Culture générale",
  "Histoire",
  "Géographie",
  "Sciences",
  "Cinéma",
  "Musique",
  "Sport",
];

export const STATUS_LABELS: Record<QuizStatus, string> = {
  "en-cours": "En cours",
  bientot: "Bientôt",
  preparation: "En préparation",
};

export const EXAMPLE_QUIZZES: Quiz[] = [
  {
    id: 1,
    title: "Capitales d'Europe",
    theme: "Géographie",
    host: "Camille",
    questionCount: 15,
    players: 8,
    status: "en-cours",
  },
  {
    id: 2,
    title: "Les années 90 au cinéma",
    theme: "Cinéma",
    host: "Hugo",
    questionCount: 20,
    players: 5,
    status: "en-cours",
  },
  {
    id: 3,
    title: "Le système solaire",
    theme: "Sciences",
    host: "Inès",
    questionCount: 10,
    players: 3,
    status: "bientot",
  },
];
