# tests/integration/test_budget_workflow.py

import pytest
from datetime import date
from src.database.db_manager import DatabaseManager
from src.services.transaction_service import TransactionService
from src.services.budget_service import BudgetService
from src.models.transaction import Transaction
from src.models.budget import Budget

class TestBudgetWorkflow:
    """Tests d'intégration pour le workflow complet de gestion de budget"""
    
    @pytest.fixture
    def setup_services(self):
        """Fixture qui initialise tous les services"""
        db = DatabaseManager(":memory:")
        transaction_service = TransactionService(db)
        budget_service = BudgetService(db, transaction_service)
        
        return {
            'db': db,
            'transaction_service': transaction_service,
            'budget_service': budget_service
        }
    
    def test_budget_lifecycle(self, setup_services):
        """Test: cycle de vie complet d'un budget"""
        services = setup_services
        budget_service = services['budget_service']
        transaction_service = services['transaction_service']
        
        # 1. Créer un budget
        budget = Budget(
            category_id=1,
            amount=500,
            period_start=date(2026, 1, 1),
            period_end=date(2026, 1, 31)
        )
        budget_id = budget_service.create_budget(budget)
        assert budget_id > 0
        
        # 2. Vérifier le statut initial
        status = budget_service.get_budget_status(1, date(2026, 1, 1), date(2026, 1, 31))
        assert status['spent'] == 0
        assert status['remaining'] == 500
        assert not status['is_exceeded']
        
        # 3. Ajouter des transactions progressivement
        t1 = Transaction(100, "Première dépense", "dépense", 1, date(2026, 1, 5))
        transaction_service.add_transaction(t1)
        
        status = budget_service.get_budget_status(1, date(2026, 1, 1), date(2026, 1, 31))
        assert status['spent'] == 100
        assert status['remaining'] == 400
        
        # 4. Ajouter plus de transactions
        t2 = Transaction(250, "Deuxième dépense", "dépense", 1, date(2026, 1, 15))
        transaction_service.add_transaction(t2)
        
        status = budget_service.get_budget_status(1, date(2026, 1, 1), date(2026, 1, 31))
        assert status['spent'] == 350
        assert status['percentage'] == 70.0
        
        # 5. Dépasser le budget
        t3 = Transaction(200, "Dépassement", "dépense", 1, date(2026, 1, 25))
        transaction_service.add_transaction(t3)
        
        status = budget_service.get_budget_status(1, date(2026, 1, 1), date(2026, 1, 31))
        assert status['is_exceeded'] is True
        assert status['remaining'] < 0
    
    def test_multiple_categories_budget(self, setup_services):
        """Test: gestion de budgets multiples"""
        services = setup_services
        budget_service = services['budget_service']
        transaction_service = services['transaction_service']
        
        # Créer des budgets pour plusieurs catégories
        b1 = Budget(1, 300, date(2026, 1, 1), date(2026, 1, 31))  # alimentation
        b2 = Budget(3, 200, date(2026, 1, 1), date(2026, 1, 31))  # loisirs
        
        budget_service.create_budget(b1)
        budget_service.create_budget(b2)
        
        # Ajouter des transactions dans chaque catégorie
        t1 = Transaction(150, "Courses", "dépense", 1, date(2026, 1, 10))
        t2 = Transaction(80, "Cinéma", "dépense", 3, date(2026, 1, 12))
        
        transaction_service.add_transaction(t1)
        transaction_service.add_transaction(t2)
        
        # Vérifier chaque budget indépendamment
        status1 = budget_service.get_budget_status(1, date(2026, 1, 1), date(2026, 1, 31))
        status2 = budget_service.get_budget_status(3, date(2026, 1, 1), date(2026, 1, 31))
        
        assert status1['spent'] == 150
        assert status2['spent'] == 80
        assert status1['percentage'] == 50.0
        assert status2['percentage'] == 40.0
    
    def test_transaction_modification_impacts_budget(self, setup_services):
        """Test: la modification d'une transaction impacte le budget"""
        services = setup_services
        budget_service = services['budget_service']
        transaction_service = services['transaction_service']
        
        # Créer un budget
        budget = Budget(1, 300, date(2026, 1, 1), date(2026, 1, 31))
        budget_service.create_budget(budget)
        
        # Ajouter une transaction
        t = Transaction(100, "Transaction initiale", "dépense", 1, date(2026, 1, 10))
        t_id = transaction_service.add_transaction(t)
        
        # Vérifier le statut
        status1 = budget_service.get_budget_status(1, date(2026, 1, 1), date(2026, 1, 31))
        assert status1['spent'] == 100
        
        # Modifier la transaction
        t_updated = Transaction(250, "Transaction modifiée", "dépense", 1, date(2026, 1, 10))
        transaction_service.update_transaction(t_id, t_updated)
        
        # Le budget doit refléter le changement
        status2 = budget_service.get_budget_status(1, date(2026, 1, 1), date(2026, 1, 31))
        assert status2['spent'] == 250
    
    def test_transaction_deletion_impacts_budget(self, setup_services):
        """Test: la suppression d'une transaction impacte le budget"""
        services = setup_services
        budget_service = services['budget_service']
        transaction_service = services['transaction_service']
        
        # Créer un budget
        budget = Budget(1, 300, date(2026, 1, 1), date(2026, 1, 31))
        budget_service.create_budget(budget)
        
        # Ajouter des transactions
        t1 = Transaction(100, "Transaction 1", "dépense", 1, date(2026, 1, 10))
        t2 = Transaction(50, "Transaction 2", "dépense", 1, date(2026, 1, 15))
        
        t1_id = transaction_service.add_transaction(t1)
        transaction_service.add_transaction(t2)
        
        # Vérifier le statut
        status1 = budget_service.get_budget_status(1, date(2026, 1, 1), date(2026, 1, 31))
        assert status1['spent'] == 150
        
        # Supprimer une transaction
        transaction_service.delete_transaction(t1_id)
        
        # Le budget doit refléter la suppression
        status2 = budget_service.get_budget_status(1, date(2026, 1, 1), date(2026, 1, 31))
        assert status2['spent'] == 50
