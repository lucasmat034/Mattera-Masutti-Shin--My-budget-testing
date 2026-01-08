# tests/unit/test_services.py

import pytest
from datetime import date
from src.models.transaction import Transaction
from src.models.budget import Budget

class TestTransactionService:
    """Tests du service de transactions"""
    
    def test_add_and_retrieve_transaction(self, transaction_service):
        """Test: ajout et récupération d'une transaction"""
        t = Transaction(
            amount=25.50,
            description="Courses",
            type="dépense",
            category_id=1,
            date=date(2026, 1, 6)
        )
        
        t_id = transaction_service.add_transaction(t)
        assert t_id > 0
        
        retrieved = transaction_service.get_transaction_by_id(t_id)
        assert retrieved.amount == 25.50
        assert retrieved.description == "Courses"
    
    def test_list_transactions_by_category(self, transaction_service):
        """Test: filtrage des transactions par catégorie"""
        # Ajouter des transactions dans différentes catégories
        t1 = Transaction(50, "Courses", "dépense", 1, date(2026, 1, 5))
        t2 = Transaction(30, "Essence", "dépense", 4, date(2026, 1, 6))
        t3 = Transaction(20, "Restaurant", "dépense", 1, date(2026, 1, 7))
        
        transaction_service.add_transaction(t1)
        transaction_service.add_transaction(t2)
        transaction_service.add_transaction(t3)
        
        # Filtrer par catégorie 1 (alimentation)
        results = transaction_service.list_transactions(category_id=1)
        assert len(results) >= 2
        assert all(t.category_id == 1 for t in results)
    
    def test_calculate_total_by_category(self, transaction_service):
        """Test: calcul du total des dépenses par catégorie"""
        # Ajouter des transactions
        t1 = Transaction(100, "Courses 1", "dépense", 1, date(2026, 1, 5))
        t2 = Transaction(150, "Courses 2", "dépense", 1, date(2026, 1, 15))
        t3 = Transaction(50, "Courses 3", "dépense", 1, date(2026, 1, 25))
        
        transaction_service.add_transaction(t1)
        transaction_service.add_transaction(t2)
        transaction_service.add_transaction(t3)
        
        # Calculer le total pour janvier
        total = transaction_service.get_total_by_category(
            category_id=1,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            transaction_type='dépense'
        )
        assert total >= 300
    
    def test_update_transaction(self, transaction_service):
        """Test: mise à jour d'une transaction"""
        # Créer une transaction
        t = Transaction(100, "Description originale", "dépense", 1, date(2026, 1, 10))
        t_id = transaction_service.add_transaction(t)
        
        # Modifier la transaction
        t_updated = Transaction(150, "Description modifiée", "dépense", 2, date(2026, 1, 11))
        success = transaction_service.update_transaction(t_id, t_updated)
        assert success is True
        
        # Vérifier les modifications
        retrieved = transaction_service.get_transaction_by_id(t_id)
        assert retrieved.amount == 150
        assert retrieved.description == "Description modifiée"
        assert retrieved.category_id == 2
    
    def test_delete_transaction(self, transaction_service):
        """Test: suppression d'une transaction"""
        # Créer une transaction
        t = Transaction(50, "À supprimer", "dépense", 1, date(2026, 1, 10))
        t_id = transaction_service.add_transaction(t)
        
        # Supprimer la transaction
        success = transaction_service.delete_transaction(t_id)
        assert success is True
        
        # Vérifier qu'elle n'existe plus
        retrieved = transaction_service.get_transaction_by_id(t_id)
        assert retrieved is None


class TestBudgetService:
    """Tests du service de budgets"""
    
    def test_create_budget(self, budget_service):
        """Test: création d'un budget"""
        b = Budget(
            category_id=1,
            amount=300,
            period_start=date(2026, 1, 1),
            period_end=date(2026, 1, 31)
        )
        
        budget_id = budget_service.create_budget(b)
        assert budget_id > 0
    
    def test_budget_status_no_spending(self, budget_service):
        """Test: statut du budget sans dépense"""
        b = Budget(1, 300, date(2026, 2, 1), date(2026, 2, 28))
        budget_service.create_budget(b)
        
        status = budget_service.get_budget_status(1, date(2026, 2, 1), date(2026, 2, 28))
        
        assert status['budget_amount'] == 300
        assert status['spent'] == 0
        assert status['remaining'] == 300
        assert status['percentage'] == 0
        assert status['is_exceeded'] is False
    
    def test_budget_status_with_spending(self, budget_service, transaction_service):
        """Test: statut du budget avec dépenses"""
        # Créer un budget
        b = Budget(1, 300, date(2026, 3, 1), date(2026, 3, 31))
        budget_service.create_budget(b)
        
        # Ajouter des dépenses
        t1 = Transaction(100, "Courses 1", "dépense", 1, date(2026, 3, 10))
        t2 = Transaction(150, "Courses 2", "dépense", 1, date(2026, 3, 20))
        transaction_service.add_transaction(t1)
        transaction_service.add_transaction(t2)
        
        # Vérifier le statut
        status = budget_service.get_budget_status(1, date(2026, 3, 1), date(2026, 3, 31))
        
        assert status['budget_amount'] == 300
        assert status['spent'] == 250
        assert status['remaining'] == 50
        assert status['percentage'] == 83.3
        assert status['is_exceeded'] is False
    
    def test_budget_exceeded(self, budget_service, transaction_service):
        """Test: détection de dépassement de budget"""
        # Créer un budget
        b = Budget(1, 300, date(2026, 4, 1), date(2026, 4, 30))
        budget_service.create_budget(b)
        
        # Ajouter des dépenses dépassant le budget
        t1 = Transaction(200, "Courses 1", "dépense", 1, date(2026, 4, 10))
        t2 = Transaction(150, "Courses 2", "dépense", 1, date(2026, 4, 20))
        transaction_service.add_transaction(t1)
        transaction_service.add_transaction(t2)
        
        # Vérifier le statut
        status = budget_service.get_budget_status(1, date(2026, 4, 1), date(2026, 4, 30))
        
        assert status['spent'] == 350
        assert status['remaining'] == -50
        assert status['is_exceeded'] is True
