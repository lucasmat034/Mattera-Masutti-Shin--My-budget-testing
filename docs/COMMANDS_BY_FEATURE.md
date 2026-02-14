# Commandes Par Fonctionnalite

Ce document liste les commandes CLI a utiliser pour chaque fonctionnalite.

**MVP**
Saisie et consultation des transactions.
```bash
mybudget add 25.50 "Courses Leclerc" alimentation 2026-01-06
mybudget list
mybudget list --category alimentation
mybudget list --start 2026-01-01 --end 2026-01-31
mybudget list --type depense
```

Gestion des budgets.
```bash
mybudget budget alimentation 300 2026-01-01 2026-01-31
mybudget status alimentation 2026-01-01 2026-01-31
```

**A. Gestion Avancee Des Transactions**
Modification d'une transaction.
```bash
mybudget update 12 --amount 50 --description "Correction"
mybudget update 12 --category loisirs --date 2026-01-15
mybudget update 12 --type revenu
```

Suppression d'une transaction.
```bash
mybudget delete 12 --yes
```

Filtres avances sur les transactions.
```bash
mybudget list --type revenu
mybudget list --start 2026-01-01 --end 2026-01-31
mybudget list --category loisirs
mybudget list --category loisirs --type depense --start 2026-01-01 --end 2026-01-31
```

**C. Export Et Persistance**
Export des transactions en CSV ou JSON.
```bash
mybudget export --format csv --output export.csv
mybudget export --format json --output export.json --pretty
mybudget export --format json --output export.json --compact
```

Export d'un resume de budget en JSON.
```bash
mybudget export-budget alimentation 2026-01-01 2026-01-31 --output budget.json
```

Reinitialisation des donnees.
```bash
mybudget reset --yes
```

Sauvegarde et chargement.
La persistance est automatique via SQLite. Le fichier est cree et mis a jour dans `data/budget.db` des la premiere utilisation.
