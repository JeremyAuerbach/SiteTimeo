---
name: verifier
description: Lancer toutes les vérifications de SiteTimeo (tests pytest, lint et format Ruff, typecheck et build du frontend) avant un commit ou pour confirmer qu'un changement ne casse rien.
---

# Vérifier le projet avant de commiter

Depuis la racine du dépôt :

```bash
# Backend
cd backend
pip install -q -r requirements-dev.txt   # si l'environnement n'est pas prêt
ruff format --check .
ruff check .
pytest -q
cd ..

# Frontend
cd frontend
npm ci        # si node_modules est absent
npm run build # inclut le typecheck (tsc -b)
cd ..
```

Pour un changement de bout en bout (auth, base, nginx), vérifier aussi la stack complète :

```bash
docker compose up -d --build
curl -sf http://localhost:8080/api/health
```

Corriger tout échec avant de commiter. Si une vérification ne peut pas tourner (outil absent,
pas de Docker), le dire explicitement à l'utilisateur plutôt que de la passer sous silence.
