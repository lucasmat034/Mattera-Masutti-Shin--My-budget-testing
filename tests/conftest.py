# tests/conftest.py
import pytest
from datetime import date
from src.database.db_manager import DatabaseManager
from src.services.transaction_service import TransactionService
from src.services.budget_service import BudgetService

@pytest.fixture
def db_manager():
    """Fixture pour une base de données de test en mémoire"""
    db = DatabaseManager(":memory:")
    yield db
    db.close()

@pytest.fixture
def transaction_service(db_manager):
    """Fixture pour le service de transactions"""
    return TransactionService(db_manager)

@pytest.fixture
def budget_service(db_manager, transaction_service):
    """Fixture pour le service de budgets"""
    return BudgetService(db_manager, transaction_service)
