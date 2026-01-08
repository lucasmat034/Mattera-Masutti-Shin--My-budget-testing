# Guide de Contribution - MyBudget

Merci de votre intérêt pour contribuer à MyBudget ! Ce document explique comment participer au développement du projet.

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.8 ou supérieur
- Git
- pip

### Installation de l'environnement de développement

```bash
# Cloner le projet
git clone <url-du-repo>
cd mybudget

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances de développement
pip install -e .
pip install -e .[dev]
```

## 🏗️ Architecture du Projet

```
src/
├── models/          # Modèles de données (Transaction, Budget, Category)
├── services/        # Logique métier
├── database/        # Gestion de la base de données
├── cli/             # Interface en ligne de commande
└── utils/           # Utilitaires

tests/
├── unit/            # Tests unitaires
├── integration/     # Tests d'intégration
└── features/        # Tests BDD (Gherkin)
```

## 📝 Workflow de Développement

### 1. Créer une branche

```bash
git checkout -b feature/ma-nouvelle-fonctionnalite
# ou
git checkout -b fix/correction-bug
```

### 2. Développer en TDD/BDD

#### TDD (Test-Driven Development)
1. Écrire le test unitaire qui échoue
2. Implémenter le code minimum pour passer le test
3. Refactorer le code

Exemple :
```python
# tests/unit/test_mon_service.py
def test_nouvelle_fonctionnalite(self, mon_service):
    result = mon_service.nouvelle_fonction()
    assert result == valeur_attendue
```

#### BDD (Behavior-Driven Development)
1. Écrire le scénario en Gherkin
2. Implémenter les steps
3. Implémenter la fonctionnalité

Exemple :
```gherkin
# tests/features/ma_fonctionnalite.feature
Feature: Ma nouvelle fonctionnalité
  Scenario: Cas d'utilisation nominal
    Given un contexte initial
    When une action est effectuée
    Then le résultat attendu est obtenu
```

### 3. Exécuter les Tests

```bash
# Tous les tests
pytest

# Tests unitaires seulement
pytest tests/unit/

# Tests avec couverture
pytest --cov=src --cov-report=html
```

### 4. Vérifier la Qualité du Code

```bash
# Linting
flake8 src/ --max-line-length=100

# Formatage
black src/ --check

# Type checking
mypy src/
```

### 5. Vérifier la Couverture

La couverture minimale requise est de **80%**.

```bash
# Générer le rapport de couverture
pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```

## 🎨 Conventions de Code

### Style Python
- Suivre PEP 8
- Longueur maximale de ligne : 100 caractères
- Utiliser Black pour le formatage automatique

### Nommage
- **Classes** : `PascalCase` (ex: `TransactionService`)
- **Fonctions/méthodes** : `snake_case` (ex: `get_transaction_by_id`)
- **Constantes** : `UPPER_CASE` (ex: `MAX_AMOUNT`)
- **Variables privées** : préfixe `_` (ex: `_internal_method`)

### Docstrings
Utiliser le format Google docstrings :

```python
def ma_fonction(param1: str, param2: int) -> bool:
    """
    Description courte de la fonction.
    
    Description détaillée si nécessaire.
    
    Args:
        param1: Description du premier paramètre
        param2: Description du second paramètre
        
    Returns:
        Description de la valeur de retour
        
    Raises:
        ValueError: Si param2 est négatif
    """
    pass
```

## 🧪 Écriture des Tests

### Tests Unitaires

Chaque classe doit avoir ses tests unitaires :

```python
class TestMaClasse:
    """Tests de MaClasse"""
    
    def test_comportement_normal(self):
        """Test: comportement dans le cas nominal"""
        # Given
        obj = MaClasse(param)
        
        # When
        result = obj.method()
        
        # Then
        assert result == expected
    
    def test_cas_limite(self):
        """Test: gestion des cas limites"""
        # ...
```

### Tests d'Intégration

Tester l'interaction entre composants :

```python
def test_workflow_complet(self, service1, service2):
    """Test: workflow complet de bout en bout"""
    # Simuler un cas d'usage réel
    # ...
```

## 🔀 Pull Requests

### Avant de soumettre

- [ ] Les tests passent (`pytest`)
- [ ] La couverture est ≥ 80% (`pytest --cov=src --cov-fail-under=80`)
- [ ] Le code est formaté (`black src/`)
- [ ] Pas d'erreurs de linting (`flake8 src/`)
- [ ] La documentation est à jour

### Format du titre

- `feat: Description de la fonctionnalité` pour une nouvelle fonctionnalité
- `fix: Description du bug` pour une correction
- `docs: Description` pour la documentation
- `test: Description` pour les tests
- `refactor: Description` pour le refactoring

### Description

Décrire clairement :
1. Quoi : Qu'est-ce qui change ?
2. Pourquoi : Pourquoi ce changement ?
3. Comment : Comment l'avez-vous implémenté ?

## 🐛 Signaler un Bug

Ouvrir une issue avec :
- Description du bug
- Étapes pour reproduire
- Comportement attendu vs observé
- Environnement (OS, version Python)
- Logs/screenshots si pertinent

## 💡 Proposer une Fonctionnalité

Ouvrir une issue "Feature Request" avec :
- Description de la fonctionnalité
- Cas d'usage
- Impact attendu
- Proposition d'implémentation (optionnel)

## 📞 Questions ?

- Ouvrir une issue "Question"
- Consulter la documentation dans `docs/`

## 📜 Licence

En contribuant, vous acceptez que votre code soit distribué sous la licence MIT du projet.

---

Merci de contribuer à MyBudget ! 🎉
