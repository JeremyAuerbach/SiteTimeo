---
name: nouvelle-branche
description: Créer une branche dédiée avant de commencer un nouvel élément du projet SiteTimeo (fonctionnalité, correction, refonte). À utiliser au début de toute nouvelle tâche qui modifiera le code, car on ne travaille jamais directement sur main.
---

# Démarrer un nouvel élément sur sa propre branche

On ne commite et ne pousse **jamais** directement sur `main`.

1. Vérifier l'état : `git status`. S'il reste des modifications non commitées qui ne concernent
   pas la nouvelle tâche, demander à l'utilisateur quoi en faire avant de continuer.
2. Partir du `main` à jour :
   ```bash
   git fetch origin main
   git checkout -B <branche> origin/main
   ```
3. Nommer la branche `<type>/<sujet-en-kebab-case>` :
   - `feature/` nouvelle fonctionnalité (ex. `feature/profil-utilisateur`)
   - `fix/` correction de bug
   - `chore/` outillage, dépendances, configuration
   - `docs/` documentation seule
4. Si la tâche continue une branche existante non fusionnée, la reprendre plutôt que d'en créer
   une nouvelle. Si sa pull request est déjà fusionnée, repartir de `main` comme ci-dessus.
5. Pousser avec `git push -u origin <branche>`. Ne créer de pull request que si l'utilisateur
   le demande.
