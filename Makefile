# Makefile pour MyBudget

.PHONY: install test coverage demo clean help

help:
	@echo "Commandes disponibles:"
	@echo "  make install   - Installer les dépendances"
	@echo "  make test      - Exécuter les tests"
	@echo "  make coverage  - Tests avec rapport de couverture"
	@echo "  make demo      - Initialiser des données de démo"
	@echo "  make clean     - Nettoyer les fichiers temporaires"
	@echo "  make quality   - Vérifier la qualité du code"

install:
	pip install -e .
	pip install -e .[dev]

test:
	pytest tests/ -v

coverage:
	pytest --cov=src --cov-report=html --cov-report=term-missing

demo:
	python scripts/init_demo_data.py

quality:
	pytest --cov=src --cov-fail-under=80
	flake8 src/ --max-line-length=100 || true
	black src/ --check || true

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage
	rm -f data/budget.db
