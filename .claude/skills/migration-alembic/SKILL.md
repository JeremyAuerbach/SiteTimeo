---
name: migration-alembic
description: Créer ou modifier une migration Alembic quand on change les modèles SQLAlchemy de SiteTimeo (nouvelle table, colonne, index, contrainte). À utiliser dès qu'on touche à backend/app/models.py.
---

# Changer le schéma de la base

Tout changement de structure passe par un fichier de migration relu et commité.

1. Modifier les modèles dans `backend/app/models.py`.
2. Générer la migration (base PostgreSQL démarrée et à jour, depuis `backend/`) :
   ```bash
   alembic upgrade head
   alembic revision --autogenerate -m "description courte en français"
   ```
   Sans base locale, l'écrire à la main en copiant la forme de
   `backend/alembic/versions/20261017_0001_users_et_sessions.py`. Numéroter `revision`
   à la suite (`0002`, `0003`…) et renseigner `down_revision` avec la précédente.
3. **Relire le fichier généré** : l'autogénération rate souvent les index sur expression
   (ex. `lower(username)`), les renommages (vus comme suppression + ajout, donc perte de données),
   les valeurs par défaut et les types énumérés. Corriger à la main.
4. Écrire un `downgrade()` qui défait exactement `upgrade()`.
5. Vérifier :
   ```bash
   alembic upgrade head && alembic downgrade -1 && alembic upgrade head
   alembic check   # doit répondre « No new upgrade operations detected »
   ```
6. Commiter le modèle et la migration ensemble.

Ne jamais modifier une migration déjà fusionnée dans `main` : en ajouter une nouvelle.
