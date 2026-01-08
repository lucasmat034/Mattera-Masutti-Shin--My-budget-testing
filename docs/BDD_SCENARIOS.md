# Scénarios BDD - MyBudget

Ce document regroupe tous les scénarios BDD (Behavior-Driven Development) du projet MyBudget.

## 📋 Table des Matières

1. [Alertes de Dépassement de Budget](#alertes-de-dépassement-de-budget)
2. [Export des Données](#export-des-données)
3. [Modification et Suppression](#modification-et-suppression)
4. [Gestion des Budgets](#gestion-des-budgets)

---

## 🔔 Alertes de Dépassement de Budget

### Feature: Alerte de dépassement de budget

**Fichier**: `tests/features/budget_alert.feature`

#### Scénario 1: Dépassement du budget alimentation
```gherkin
Given un budget de 300 € pour la catégorie "alimentation" du 2026-01-01 au 2026-01-31
And des dépenses existantes de 290 € en "alimentation"
When j'ajoute une nouvelle dépense de 20 € en "alimentation"
Then le total des dépenses est de 310 €
And le budget est dépassé de 10 €
And une alerte est affichée à l'utilisateur
And l'alerte indique un dépassement de 103.3%
```

**Objectif**: Vérifier qu'une alerte est affichée quand un budget est dépassé.

#### Scénario 2: Budget proche de la limite (80%)
```gherkin
Given un budget de 500 € pour la catégorie "loisirs" du 2026-01-01 au 2026-01-31
And des dépenses existantes de 350 € en "loisirs"
When j'ajoute une nouvelle dépense de 50 € en "loisirs"
Then le total des dépenses est de 400 €
And le budget n'est pas dépassé
But un avertissement de proximité est affiché (80%)
```

**Objectif**: Alerter l'utilisateur quand il atteint 80% du budget.

#### Scénario 3: Budget non dépassé avec marge confortable
```gherkin
Given un budget de 1000 € pour la catégorie "logement" du 2026-01-01 au 2026-01-31
And des dépenses existantes de 200 € en "logement"
When j'ajoute une nouvelle dépense de 100 € en "logement"
Then le total des dépenses est de 300 €
And le budget n'est pas dépassé
And aucune alerte n'est affichée
```

**Objectif**: Vérifier qu'aucune alerte n'est affichée si le budget est confortable.

---

## 📊 Export des Données

### Feature: Export des données

**Fichier**: `tests/features/export.feature`

#### Scénario 1: Export de toutes les transactions en CSV
```gherkin
Given j'ai 5 transactions dans ma base de données
When j'exporte toutes les transactions en CSV vers "export.csv"
Then le fichier "export.csv" contient 5 lignes de données
And le fichier CSV contient les colonnes: id, date, amount, description, type, category_id
```

**Objectif**: Exporter toutes les transactions au format CSV.

#### Scénario 2: Export filtré par catégorie en JSON
```gherkin
Given j'ai des transactions dans 3 catégories différentes
When j'exporte les transactions de la catégorie "alimentation" en JSON
Then le fichier JSON contient uniquement les transactions de cette catégorie
And le JSON contient le nombre total de transactions exportées
```

**Objectif**: Exporter uniquement les transactions d'une catégorie spécifique.

#### Scénario 3: Export d'un résumé de budget
```gherkin
Given un budget de 500 € pour "loisirs" en janvier 2026
And des dépenses de 350 € en "loisirs" en janvier
When j'exporte le résumé du budget en JSON
Then le fichier contient le statut du budget
And le fichier contient la liste des transactions de la période
```

**Objectif**: Exporter un rapport complet de budget.

---

## 🔄 Modification et Suppression

### Feature: Modification et suppression de transactions

**Fichier**: `tests/features/modification.feature`

#### Scénario 1: Modification du montant d'une transaction
```gherkin
Given une transaction de 100 € pour "Courses" en alimentation
When je modifie le montant à 150 €
Then la transaction affiche un montant de 150 €
And le total des dépenses est mis à jour
```

**Objectif**: Modifier le montant d'une transaction existante.

#### Scénario 2: Suppression d'une transaction
```gherkin
Given une transaction de 50 € pour "Restaurant"
And le total des dépenses en alimentation est de 250 €
When je supprime cette transaction
Then la transaction n'existe plus
And le total des dépenses en alimentation est de 200 €
```

**Objectif**: Supprimer une transaction et vérifier l'impact sur les totaux.

#### Scénario 3: Modification de la catégorie d'une transaction
```gherkin
Given une transaction de 30 € classée en "loisirs"
When je change la catégorie vers "alimentation"
Then la transaction est dans la catégorie "alimentation"
And le total de "loisirs" a diminué de 30 €
And le total de "alimentation" a augmenté de 30 €
```

**Objectif**: Changer la catégorie d'une transaction et vérifier la cohérence.

---

## 💰 Gestion des Budgets

### Feature: Gestion de budgets

#### Scénario 1: Création d'un budget mensuel
```gherkin
Given je suis un utilisateur connecté
When je crée un budget de 300 € pour "alimentation" du 01/01/2026 au 31/01/2026
Then le budget est enregistré
And je peux consulter ce budget
```

**Objectif**: Créer un nouveau budget pour une catégorie.

#### Scénario 2: Suivi de plusieurs budgets
```gherkin
Given j'ai un budget de 300 € pour "alimentation"
And j'ai un budget de 200 € pour "loisirs"
And j'ai un budget de 800 € pour "logement"
When je consulte mes budgets
Then je vois les 3 budgets
And chaque budget affiche son pourcentage de consommation
```

**Objectif**: Gérer plusieurs budgets simultanément.

---

## 🎯 Bonnes Pratiques BDD

### Format Gherkin

Chaque scénario suit la structure :
- **Given** (Étant donné) : Contexte initial
- **When** (Quand) : Action effectuée
- **Then** (Alors) : Résultat attendu
- **And** (Et) : Conditions supplémentaires

### Principes

1. **Langage naturel** : Compréhensible par tous
2. **Indépendance** : Chaque scénario est autonome
3. **Clarté** : Un scénario teste un comportement précis
4. **Réutilisabilité** : Les steps sont réutilisables

### Implémentation

Chaque scénario est associé à :
- Un fichier `.feature` (spécification)
- Un fichier `*_steps.py` (implémentation des steps)
- Des tests unitaires associés

---

## 📈 Couverture des Tests

| Feature | Scénarios | Steps | Statut |
|---------|-----------|-------|--------|
| Alertes de budget | 3 | 15 | ✅ Complet |
| Export | 3 | 12 | ✅ Complet |
| Modification | 3 | 12 | ✅ Complet |
| Gestion budgets | 2 | 8 | ✅ Complet |

**Total**: 11 scénarios, ~47 steps implémentés

---

## 🔗 Ressources

- [Cucumber/Gherkin Syntax](https://cucumber.io/docs/gherkin/)
- [pytest-bdd Documentation](https://pytest-bdd.readthedocs.io/)
- [BDD Best Practices](https://cucumber.io/docs/bdd/)

---

Dernière mise à jour : 8 janvier 2026
