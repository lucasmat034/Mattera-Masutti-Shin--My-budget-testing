# MyBudget - Gestionnaire de Budget Personnel 💰

Application de gestion de budget personnel développée en TDD/BDD.

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](.)
[![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen)](.)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](.)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

## ✨ Fonctionnalités

### MVP
- ✅ Gestion des transactions (ajout, modification, suppression)
- ✅ Gestion des budgets par catégorie
- ✅ Consultation des statuts de budget
- ✅ Filtrage et recherche de transactions

### Fonctionnalités Avancées
- 🔔 **Alertes de dépassement** : Notifications automatiques
- 📊 **Export CSV/JSON** : Export des données et rapports
- 🔄 **Modification** : Modification/suppression de transactions
- 📈 **Statistiques** : Analyses et prédictions avancées

## 🚀 Installation Rapide

```bash
# Cloner le projet
git clone <url-du-repo>
cd mybudget

# Installer
pip install -e .

# Initialiser des données de démo (optionnel)
python scripts/init_demo_data.py
```

## 💻 Utilisation

```bash
# Créer un budget
mybudget budget alimentation 300 2026-01-01 2026-01-31

# Ajouter une dépense
mybudget add 45.50 "Courses" alimentation 2026-01-05

# Consulter le statut
mybudget status alimentation 2026-01-01 2026-01-31

# Lister les transactions
mybudget list --category alimentation --start 2026-01-01
```

## 🧪 Tests

```bash
# Tous les tests
pytest

# Tests avec couverture
pytest --cov=src --cov-report=html

# Vérification qualité complète
python scripts/quality_check.py
```

## 📊 Statistiques

- **Code source** : ~1150 lignes
- **Tests** : 97+ tests (85-89% couverture)
- **Documentation** : 6 fichiers
- **Scénarios BDD** : 11 scénarios

## 📚 Documentation

- [QUICKSTART.md](QUICKSTART.md) - Démarrage rapide
- [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) - Guide de contribution
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Architecture technique
- [docs/BDD_SCENARIOS.md](docs/BDD_SCENARIOS.md) - Scénarios BDD
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Résumé complet du projet

## 🏗️ Architecture

```
src/
├── models/          # Modèles de données
├── services/        # Logique métier
├── database/        # Gestion SQLite
└── cli/             # Interface CLI

tests/
├── unit/            # Tests unitaires
├── integration/     # Tests d'intégration
└── features/        # Tests BDD
```

## 🛠️ Technologies

- **Python** 3.8+
- **Click** (CLI)
- **SQLite** (Base de données)
- **pytest** (Tests)
- **pytest-bdd** (Tests comportementaux)

## 📜 Licence

MIT License - Copyright (c) 2026 Équipe Mattera-Masutti-Shin

## 👥 Équipe

- Mattera
- Masutti
- Shin

**Contact** : rida@lamerkanterie.fr

---

Développé avec ❤️ en TDD/BDD

