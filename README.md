MyBudget — Gestionnaire de budget en ligne de commande
======================================================
Application Python (≥3.8) pour suivre vos revenus/dépenses, créer des budgets par catégorie et recevoir des alertes de dépassement. Développée en TDD/BDD, licence MIT, équipe Mattera‑Masutti‑Shin.
Contenu du dépôt
- CLI : `src/cli/main.py` (commande `mybudget`)
- Services métier : `src/services/` (transactions, budgets, exports, statistiques)
- Modèles : `src/models/` (dataclasses avec validations)
- Accès données : `src/database/db_manager.py` (SQLite `data/budget.db`, catégories par défaut)
- Scripts : `scripts/` (données de démo, couverture, qualité)
- Tests : `tests/` (unitaires, intégration, BDD)

Prérequis
- Python 3.8 ou plus récent
- pip et, recommandé, un environnement virtuel
- Système compatible SQLite (embarqué par défaut)

Installation rapide
```bash
python -m venv .venv
.\.venv\Scripts\activate             # Windows
pip install -e .
# Pour le dev (tests, lint, coverage)
pip install -e .[dev]
```

Premiers pas
```bash
mybudget --help
mybudget list                        # aucune transaction au début
```
La base `data/budget.db` est créée automatiquement avec les catégories : alimentation, logement, loisirs, transports, santé, autres.

Commandes disponibles (CLI Click)
- `mybudget add <montant> "<description>" <categorie> [date] [--type depense|revenu]`
  - Date optionnelle au format ISO `YYYY-MM-DD` (défaut : aujourd’hui)
  - Exemple : `mybudget add 45.50 "Courses Leclerc" alimentation 2026-01-05`
- `mybudget list [--category <cat>] [--start <YYYY-MM-DD>] [--end <YYYY-MM-DD>] [--type depense|revenu]`
  - Affiche un tableau tabulé, ordre anti‑chronologique
- `mybudget update <id> [--amount <montant>] [--description <texte>] [--category <categorie>] [--date <YYYY-MM-DD>] [--type depense|revenu]`
  - Modifie une transaction existante
- `mybudget delete <id> [--yes]`
  - Supprime une transaction
- `mybudget budget <categorie> <montant> <date_debut> <date_fin>`
  - Crée un budget pour une période donnée
- `mybudget status <categorie> <date_debut> <date_fin>`
  - Montant, dépensé, restant, %, alerte à 80 % et en cas de dépassement
- `mybudget export --format <csv|json> --output <fichier> [--category <cat>] [--start <YYYY-MM-DD>] [--end <YYYY-MM-DD>]`
  - Exporte les transactions en CSV/JSON
- `mybudget export-budget <categorie> <date_debut> <date_fin> --output <fichier>`
  - Exporte un resume de budget en JSON
- `mybudget reset [--yes]`
  - Reinitialise transactions et budgets (categories conservees)

Exemple de session
```bash
mybudget budget alimentation 300 2026-01-01 2026-01-31
mybudget add 25.90 "Déjeuner" alimentation 2026-01-03
mybudget add 180 "Courses semaine" alimentation 2026-01-05
mybudget status alimentation 2026-01-01 2026-01-31
mybudget list --category alimentation --start 2026-01-01 --end 2026-01-31
```
Les alertes de dépassement s’affichent automatiquement après chaque `add` si un budget actif est franchi.

Exports et statistiques
- Services prêts à l’emploi dans `src/services/export_service.py` et `statistics_service.py` (CSV/JSON, résumés, tendances, projections). Ils peuvent être appelés depuis du code Python ou branchés à d’autres interfaces.
Exemples CLI :
```bash
mybudget export --format csv --output export.csv
mybudget export --format json --output export.json --pretty
mybudget export-budget alimentation 2026-01-01 2026-01-31 --output budget.json

```
Données et réinitialisation
- Fichier SQLite : `data/budget.db` (créé au premier lancement).
- Réinitialiser/démarrer avec des données de démo :
  ```bash
  python scripts/init_demo_data.py
  ```
- Supprimer la base pour repartir de zéro : effacer `data/budget.db`.
- Reinitialiser les donnees (transactions/budgets) :
  ```bash
  mybudget reset --yes
  ```

Tests et qualité
- `make test`          : pytest sur `tests/`
- `make coverage`      : couverture HTML dans `tests/htmlcov`
- `make quality`       : couverture minimale 80 %, flake8, black (mode check)
- `make demo`          : remplit la base avec des données exemples
- Commandes directes : `pytest -v`, `pytest --cov=src --cov-report=term-missing`

Support rapide
- Questions fréquentes et architecture : `PROJECT_SUMMARY.md` et `docs/ARCHITECTURE.md`
- Scénarios BDD : `docs/BDD_SCENARIOS.md`
- Contribution : `docs/CONTRIBUTING.md`

Licence
- MIT License (voir `LICENSE`).

