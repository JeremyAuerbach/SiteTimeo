export type User = {
  id: number;
  username: string;
  is_guest: boolean;
  created_at: string;
};

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    throw new ApiError(response.status, await errorMessage(response));
  }
  return response.status === 204 ? (undefined as T) : response.json();
}

async function errorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body.detail === "string") return body.detail;
    // Erreur de validation FastAPI/Pydantic : liste d'erreurs par champ.
    if (Array.isArray(body.detail)) return validationMessage(body.detail[0]);
  } catch {
    // Réponse sans JSON : message générique ci-dessous.
  }
  return "Une erreur est survenue, réessaie plus tard.";
}

function validationMessage(error: { loc?: string[]; type?: string }): string {
  const field = error.loc?.at(-1);
  if (field === "username") {
    return "Le pseudo doit faire de 3 à 32 caractères : lettres, chiffres, « _ », « - » ou « . ».";
  }
  if (field === "password") return "Le mot de passe doit faire au moins 8 caractères.";
  return "Les informations saisies sont invalides.";
}

const post = <T>(path: string, body?: unknown) =>
  request<T>(path, { method: "POST", body: body === undefined ? undefined : JSON.stringify(body) });

export const api = {
  me: () => request<User>("/auth/me"),
  login: (username: string, password: string) => post<User>("/auth/login", { username, password }),
  register: (username: string, password: string) =>
    post<User>("/auth/register", { username, password }),
  guest: (username: string) => post<User>("/auth/guest", { username }),
  logout: () => post<void>("/auth/logout"),
};
