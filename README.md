# SiteTimeo

Site web avec connexion par pseudo + mot de passe, ou en visiteur (compte temporaire).

## Démarrer (machine vierge)

Seul prérequis : Docker (avec Docker Compose).

```bash
docker compose up --build
```

Puis ouvrir http://localhost:8080. La documentation de l'API est sur http://localhost:8080/api/docs.

Les réglages (port, identifiants PostgreSQL…) ont des valeurs par défaut ; pour les changer,
copier `.env.example` en `.env`.

## Structure

```
backend/            API FastAPI (Python 3.13)
  app/
    main.py         Application, tâche de nettoyage des visiteurs
    config.py       Réglages (variables d'environnement)
    models.py       Tables SQLAlchemy
    schemas.py      Schémas Pydantic (entrées / sorties de l'API)
    auth.py         Sessions : création, lecture du cookie, expiration
    routers/        Routes de l'API (auth.py : connexion, account.py : compte et photo)
  alembic/          Migrations du schéma de base
  tests/            Tests pytest
frontend/           Écrans React + TypeScript (Vite), servis par nginx
  src/pages/        Connexion, accueil (menu à gauche) et ses onglets Quizz et Compte
  src/quiz/         Quizz d'exemple, en attendant le backend des quizz
docker-compose.yml  PostgreSQL 16 + backend + frontend
```

## Comptes

- **Compte classique** : pseudo (3 à 32 caractères, lettres, chiffres, `_ - .`) et mot de passe
  (8 caractères minimum). Les pseudos sont uniques sans tenir compte des majuscules.
- **Visiteur** : choisit seulement un pseudo. Son compte est supprimé :
  - dès qu'il se déconnecte ;
  - sinon, quand il ferme l'application : la page signale sa présence chaque minute, et après
    10 minutes sans signe de vie le serveur supprime le compte (le pseudo redevient libre).
    Le cookie du visiteur est en plus un cookie de session, effacé à la fermeture du navigateur.

Depuis l'onglet **Compte**, on peut ajouter une photo de profil (recadrée au carré et réduite à
256 px avant l'envoi, 2 Mo maximum, stockée en base), changer de pseudo et, pour un compte
classique, changer de mot de passe (les autres appareils connectés sont alors déconnectés).

La session est un jeton aléatoire dans un cookie `HttpOnly` ; la base n'en garde que l'empreinte
SHA-256. Les mots de passe sont hachés avec Argon2.

## Développer sans Docker

```bash
# Base de données seule
docker compose up -d db   # (exposer le port 5432 au besoin)

# Backend
cd backend
python3.13 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend (autre terminal) : http://localhost:5173, /api relayé vers le backend
cd frontend
npm install
npm run dev
```

## Qualité

```bash
cd backend
pytest          # tests (SQLite en mémoire ; TEST_DATABASE_URL=... pour viser PostgreSQL)
ruff check .    # lint
ruff format .   # mise en forme

cd frontend
npm run typecheck
```

## Règles de travail

- Jamais de commit direct sur `main` : chaque nouvel élément part d'une branche dédiée.
- Toute modification du schéma de base passe par une migration Alembic relue et commitée,
  jamais par une modification à la main dans la base.
