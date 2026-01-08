#!/usr/bin/env python3
"""
Script d'initialisation automatique du projet MyBudget
Ce script crée toute la structure de fichiers et dossiers nécessaire

Usage:
    python setup_project.py
"""

import os
from pathlib import Path

# Définition de la structure complète
PROJECT_STRUCTURE = {
    "directories": [
        "src/models",
        "src/services",
        "src/database",
        "src/cli",
        "src/utils",
        "tests/unit",
        "tests/integration",
        "tests/features/steps",
        "docs",
        "scripts",
        "data",
        ".github/workflows"
    ],

    "init_files": [
        "src/__init__.py",
        "src/models/__init__.py",
        "src/services/__init__.py",
        "src/database/__init__.py",
        "src/cli/__init__.py",
        "src/utils/__init__.py",
        "tests/__init__.py",
        "tests/unit/__init__.py",
        "tests/integration/__init__.py",
        "tests/features/__init__.py",
        "tests/features/steps/__init__.py",
        "scripts/__init__.py"
    ],

    "placeholder_files": [
        "data/.gitkeep"
    ]
}

# Contenu des fichiers de configuration
FILE_CONTENTS = {
    ".gitignore": """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
*.cover

# Database
data/*.db
data/*.sqlite3
!data/.gitkeep

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# OS
Thumbs.db
*.log

# Jupyter
.ipynb_checkpoints
""",

    ".python-version": "3.8\n",

    "requirements.txt": """# Core dependencies
click>=8.1.0
tabulate>=0.9.0
python-dateutil>=2.8.2

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-bdd>=6.1.1

# Development
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0
""",

    "pytest.ini": """[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
""",

    "setup.py": """from setuptools import setup, find_packages

setup(
    name="mybudget",
    version="1.0.0",
    description="Application de gestion de budget personnel",
    author="Votre Groupe",
    author_email="rida@lamerkanterie.fr",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click>=8.1.0',
        'tabulate>=0.9.0',
        'python-dateutil>=2.8.2',
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'pytest-bdd>=6.1.1',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'mybudget=src.cli.main:cli',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
""",

    "Makefile": """# Makefile pour MyBudget

.PHONY: install test coverage demo clean help

help:
\t@echo "Commandes disponibles:"
\t@echo "  make install   - Installer les dépendances"
\t@echo "  make test      - Exécuter les tests"
\t@echo "  make coverage  - Tests avec rapport de couverture"
\t@echo "  make demo      - Initialiser des données de démo"
\t@echo "  make clean     - Nettoyer les fichiers temporaires"
\t@echo "  make quality   - Vérifier la qualité du code"

install:
\tpip install -e .
\tpip install -e .[dev]

test:
\tpytest tests/ -v

coverage:
\tpytest --cov=src --cov-report=html --cov-report=term-missing

demo:
\tpython scripts/init_demo_data.py

quality:
\tpytest --cov=src --cov-fail-under=80
\tflake8 src/ --max-line-length=100 || true
\tblack src/ --check || true

clean:
\tfind . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
\tfind . -type f -name "*.pyc" -delete
\trm -rf .pytest_cache htmlcov .coverage
\trm -f data/budget.db
""",

    "LICENSE": """MIT License

Copyright (c) 2026 Votre Équipe

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""",

    ".github/workflows/tests.yml": """name: Tests

on:
  push:
    branches: [ main, feature-* ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', 3.11]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
        pip install -e .[dev]

    - name: Run tests with coverage
      run: |
        pytest --cov=src --cov-report=xml --cov-report=term-missing

    - name: Check coverage threshold
      run: |
        pytest --cov=src --cov-fail-under=80
""",

    "data/.gitkeep": "# Keep this directory in Git\n",
}


def create_directory(path: str) -> None:
    """Crée un répertoire s'il n'existe pas"""
    Path(path).mkdir(parents=True, exist_ok=True)
    print(f"✅ Créé: {path}/")


def create_file(path: str, content: str = "") -> None:
    """Crée un fichier avec du contenu"""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ Créé: {path}")


def setup_project():
    """Configure toute la structure du projet"""

    print("\n" + "=" * 60)
    print("🚀 Initialisation du projet MyBudget")
    print("=" * 60 + "\n")

    # 1. Créer les répertoires
    print("📁 Création des répertoires...")
    for directory in PROJECT_STRUCTURE["directories"]:
        create_directory(directory)

    print()

    # 2. Créer les fichiers __init__.py
    print("📄 Création des fichiers __init__.py...")
    for init_file in PROJECT_STRUCTURE["init_files"]:
        create_file(init_file, "")

    print()

    # 3. Créer les fichiers de configuration
    print("⚙️  Création des fichiers de configuration...")
    for filename, content in FILE_CONTENTS.items():
        create_file(filename, content)

    print()

    # 4. Créer les fichiers placeholder
    print("📝 Création des fichiers placeholder...")
    for placeholder in PROJECT_STRUCTURE["placeholder_files"]:
        create_file(placeholder, FILE_CONTENTS.get(placeholder, ""))

    print()

    # 5. Créer les README de base
    print("📖 Création des README...")

    readme_base = """# MyBudget - Gestionnaire de Budget Personnel

Application de gestion de budget personnel développée en TDD/BDD.

## Installation

```bash
pip install -e .
```

## Utilisation

```bash
mybudget --help
```

## Tests

```bash
pytest
```

Pour plus d'informations, consultez les fichiers:
- QUICKSTART.md - Démarrage rapide
- docs/CONTRIBUTING.md - Guide de contribution
- PROJECT_SUMMARY.md - Résumé complet du projet
"""

    create_file("README.md", readme_base)

    quickstart = """# 🚀 Guide de Démarrage Rapide

## Installation en 3 minutes

1. **Installer les dépendances**
```bash
pip install -e .
```

2. **Exécuter les tests**
```bash
pytest
```

3. **Utiliser l'application**
```bash
mybudget budget alimentation 300 2026-01-01 2026-01-31
mybudget add 45.50 "Courses" alimentation 2026-01-05
mybudget status alimentation 2026-01-01 2026-01-31
```

Consultez le README.md pour plus d'informations.
"""

    create_file("QUICKSTART.md", quickstart)

    print()
    print("=" * 60)
    print("✨ Structure du projet créée avec succès !")
    print("=" * 60)
    print()
    print("📋 Prochaines étapes:")
    print("   1. Copier le code source dans src/")
    print("   2. Copier les tests dans tests/")
    print("   3. Copier les scripts dans scripts/")
    print("   4. Copier la documentation dans docs/")
    print("   5. Installer: pip install -e .")
    print("   6. Tester: pytest")
    print("   7. Commit: git add . && git commit -m 'feat: Initial project setup'")
    print()

    # Afficher la structure créée
    print("📁 Structure créée:")
    print()

    def print_tree(directory: Path, prefix: str = "", is_last: bool = True):
        """Affiche l'arborescence des fichiers"""
        if directory.name.startswith('.') and directory.name not in ['.github', '.gitkeep']:
            return

        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{directory.name}")

        if directory.is_dir():
            children = sorted(list(directory.iterdir()), key=lambda x: (not x.is_dir(), x.name))
            # Filtrer les dossiers cachés sauf .github
            children = [c for c in children if not c.name.startswith('.') or c.name == '.github']

            for i, child in enumerate(children):
                is_last_child = i == len(children) - 1
                extension = "    " if is_last else "│   "
                print_tree(child, prefix + extension, is_last_child)

    print_tree(Path('.'))


if __name__ == "__main__":
    try:
        setup_project()
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        print("\nAssurez-vous d'exécuter ce script dans un répertoire vide ou nouveau.")