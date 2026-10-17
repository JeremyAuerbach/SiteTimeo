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

Pour un changement de bout en bout (auth, base, nginx, Docker), lancer aussi le test de fumée :

```bash
./scripts/smoke-test.sh
```

Il construit et démarre toute l'app dans un projet Docker à part (port 8089, l'instance
habituelle n'est pas touchée), vérifie les parcours essentiels et nettoie à la fin. Tout nouveau
parcours important ou toute panne rencontrée sous Docker doit y gagner une vérification.

Sur PostgreSQL (migrations comprises) :

```bash
TEST_DATABASE_URL=postgresql+psycopg://timeo:timeo@localhost:5432/timeo_test pytest -q
```

Corriger tout échec avant de commiter. Si une vérification ne peut pas tourner (outil absent,
pas de Docker), le dire explicitement à l'utilisateur plutôt que de la passer sous silence.
