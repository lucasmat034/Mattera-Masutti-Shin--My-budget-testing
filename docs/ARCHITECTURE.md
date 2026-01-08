# Architecture - MyBudget

## 📐 Vue d'Ensemble

MyBudget suit une architecture en couches (layered architecture) pour séparer les responsabilités et faciliter la maintenance.

```
┌─────────────────────────────────────────┐
│          CLI Interface (Click)          │  ← Interface utilisateur
├─────────────────────────────────────────┤
│         Services (Business Logic)        │  ← Logique métier
├─────────────────────────────────────────┤
│           Models (Data Models)           │  ← Modèles de données
├─────────────────────────────────────────┤
│     Database Manager (Persistence)       │  ← Accès aux données
├─────────────────────────────────────────┤
│           SQLite Database                │  ← Stockage
└─────────────────────────────────────────┘
```

## 🏗️ Couches de l'Application

### 1. Couche Présentation (CLI)

**Localisation**: `src/cli/`

**Responsabilités**:
- Interface en ligne de commande
- Parsing des arguments
- Affichage formaté des résultats
- Gestion des erreurs utilisateur

**Technologies**:
- Click (framework CLI)
- Tabulate (formatage de tableaux)

**Commandes principales**:
```bash
mybudget add <montant> <description> <catégorie> [date]
mybudget list [--category] [--start] [--end]
mybudget budget <catégorie> <montant> <date_début> <date_fin>
mybudget status <catégorie> <date_début> <date_fin>
```

### 2. Couche Services

**Localisation**: `src/services/`

**Services disponibles**:

#### TransactionService
- Gestion CRUD des transactions
- Filtrage et recherche
- Calculs de totaux
- Modification et suppression

#### BudgetService
- Gestion des budgets
- Calcul du statut (dépensé, restant, %)
- Détection des dépassements

#### ExportService
- Export CSV/JSON
- Export de rapports
- Formatage des données

#### StatisticsService
- Analyses statistiques
- Tendances mensuelles
- Moyennes et projections
- Top dépenses

### 3. Couche Modèles

**Localisation**: `src/models/`

#### Transaction
```python
@dataclass
class Transaction:
    amount: float          # Montant
    description: str       # Description
    type: str             # 'revenu' ou 'dépense'
    category_id: int      # ID de la catégorie
    date: date            # Date de la transaction
    id: Optional[int]     # ID unique
```

**Validations**:
- Montant > 0
- Type valide (revenu/dépense)
- Description non vide

#### Budget
```python
@dataclass
class Budget:
    category_id: int       # ID de la catégorie
    amount: float          # Montant du budget
    period_start: date     # Début de période
    period_end: date       # Fin de période
    id: Optional[int]      # ID unique
```

**Validations**:
- Montant > 0
- Date début < Date fin

#### Category
```python
@dataclass
class Category:
    name: str              # Nom de la catégorie
    id: Optional[int]      # ID unique
```

**Catégories par défaut**:
- alimentation
- logement
- loisirs
- transports
- santé
- autres

### 4. Couche Database

**Localisation**: `src/database/`

#### DatabaseManager
- Connexion SQLite
- Exécution de requêtes
- Gestion des transactions
- Création du schéma

**Schéma de la base de données**:

```sql
-- Table des catégories
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Table des transactions
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    description TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('revenu', 'dépense')),
    category_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Table des budgets
CREATE TABLE budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

## 🔄 Flux de Données

### Exemple: Ajout d'une Transaction

```
1. Utilisateur: mybudget add 50 "Courses" alimentation 2026-01-10
                    ↓
2. CLI: Parse les arguments, récupère category_id
                    ↓
3. CLI: Crée un objet Transaction (validation)
                    ↓
4. TransactionService: add_transaction()
                    ↓
5. DatabaseManager: execute_update() (INSERT)
                    ↓
6. SQLite: Stockage persistant
                    ↓
7. CLI: Affiche confirmation
                    ↓
8. CLI: Vérifie si budget dépassé (appel BudgetService)
```

### Exemple: Consultation de Statut

```
1. Utilisateur: mybudget status alimentation 2026-01-01 2026-01-31
                    ↓
2. CLI: Parse, récupère category_id
                    ↓
3. BudgetService: get_budget_status()
                    ↓
4. DatabaseManager: Requête SELECT budget
                    ↓
5. TransactionService: get_total_by_category()
                    ↓
6. DatabaseManager: Requête SUM(amount)
                    ↓
7. BudgetService: Calcule spent, remaining, percentage
                    ↓
8. CLI: Formate et affiche avec Tabulate
```

## 🎯 Principes de Conception

### SOLID

✅ **Single Responsibility**: Chaque classe a une seule responsabilité
- `TransactionService` → Gestion des transactions uniquement
- `DatabaseManager` → Accès aux données uniquement

✅ **Open/Closed**: Ouvert à l'extension, fermé à la modification
- Ajout de nouveaux services sans modifier les existants

✅ **Liskov Substitution**: Les sous-types sont substituables
- Tous les services implémentent des interfaces cohérentes

✅ **Interface Segregation**: Interfaces spécifiques
- Pas de dépendances inutiles entre couches

✅ **Dependency Inversion**: Dépendre des abstractions
- Services dépendent de `DatabaseManager` (abstraction)

### DRY (Don't Repeat Yourself)

- Code réutilisable dans les services
- Fixtures pytest partagées dans `conftest.py`
- Validations centralisées dans les modèles

### Separation of Concerns

- **Présentation** séparée de la **logique métier**
- **Logique métier** séparée de l'**accès aux données**
- **Tests** séparés par type (unit/integration/bdd)

## 📦 Dépendances

### Production
```
click ≥ 8.1.0          # Framework CLI
tabulate ≥ 0.9.0       # Formatage tableaux
python-dateutil ≥ 2.8  # Manipulation dates
```

### Développement
```
pytest ≥ 7.4.0         # Framework de tests
pytest-cov ≥ 4.1.0     # Couverture de code
pytest-bdd ≥ 6.1.1     # Tests comportementaux
black ≥ 23.0.0         # Formatage automatique
flake8 ≥ 6.0.0         # Linter
mypy ≥ 1.0.0           # Type checking
```

## 🧪 Architecture des Tests

### Tests Unitaires
- **Localisation**: `tests/unit/`
- **Cible**: Fonctions et méthodes isolées
- **Mock**: DatabaseManager en mémoire (`:memory:`)

### Tests d'Intégration
- **Localisation**: `tests/integration/`
- **Cible**: Interactions entre composants
- **Scope**: Workflows complets

### Tests BDD
- **Localisation**: `tests/features/`
- **Format**: Gherkin (`.feature`)
- **Steps**: `tests/features/steps/`

## 🔐 Sécurité et Validation

### Validation des Entrées
- Tous les modèles validés via `__post_init__`
- Requêtes SQL paramétrées (protection SQL injection)
- Validation des types avec dataclasses

### Gestion des Erreurs
- Exceptions spécifiques levées par les modèles
- Catch dans la couche CLI
- Messages d'erreur utilisateur friendly

## 📈 Performance

### Optimisations
- Index sur `category_id` et `date` (transactions)
- Requêtes avec filtres SQL (pas de filtrage en mémoire)
- Connection pooling SQLite

### Limitations
- Base SQLite locale (monothread)
- Adapté pour usage personnel (<10k transactions)

## 🔮 Évolutions Futures

### Possibles Extensions
- API REST (Flask/FastAPI)
- Interface web
- Multi-utilisateurs
- Synchronisation cloud
- Support PostgreSQL/MySQL
- Import bancaire (OFX, CSV)

---

Dernière mise à jour : 8 janvier 2026
