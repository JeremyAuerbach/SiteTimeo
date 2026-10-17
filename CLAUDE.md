# SiteTimeo — consignes pour Claude

Langue du projet : français (interface, messages d'erreur, docs, messages de commit).

## Pile technique

Python 3.13, FastAPI, Pydantic, SQLAlchemy 2, Alembic, PostgreSQL 16, React + TypeScript (Vite),
Docker Compose, pytest, Ruff. Ne pas introduire d'autre brique sans en parler à l'utilisateur.

## Règles

- **Ne jamais pousser sur `main`.** Chaque nouvel élément commence sur une branche dédiée
  (skill `nouvelle-branche`).
- **Schéma de base = migrations Alembic** dans `backend/alembic/versions/`, relues et commitées
  (skill `migration-alembic`). Jamais de modification manuelle de la base, jamais de
  `Base.metadata.create_all` hors des tests.
- Avant de commiter : skill `verifier` (tests, Ruff, typecheck, build, test de fumée Docker).
  La CI (`.github/workflows/ci.yml`) refait ces vérifications sur chaque pull request.
- Ne jamais commiter `.env` ni de secret.

## Repères

- Le frontend appelle toujours `/api/...` en même origine (nginx en prod, proxy Vite en dev) :
  les cookies de session en dépendent, ne pas passer à une URL absolue.
- Une route qui exige un utilisateur connecté dépend de `get_current_user` (`backend/app/auth.py`).
- Les visiteurs (`User.is_guest`) n'ont pas de mot de passe et sont supprimés par
  `purge_expired` quand leur session expire.
