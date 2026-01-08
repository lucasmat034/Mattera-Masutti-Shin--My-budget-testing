# tests/unit/test_modification.py

import pytest
from datetime import date
from src.models.transaction import Transaction

class TestTransactionModification:
    """Tests pour la modification et suppression de transactions"""
    
    def test_update_transaction_amount(self, transaction_service):
        """Test: mise à jour du montant d'une transaction"""
        # Créer une transaction
        t = Transaction(100, "Original", "dépense", 1, date(2026, 1, 10))
        t_id = transaction_service.add_transaction(t)
        
        # Modifier le montant
        t_updated = Transaction(150, "Original", "dépense", 1, date(2026, 1, 10))
        success = transaction_service.update_transaction(t_id, t_updated)
        
        assert success is True
        retrieved = transaction_service.get_transaction_by_id(t_id)
        assert retrieved.amount == 150
    
    def test_update_transaction_description(self, transaction_service):
        """Test: mise à jour de la description"""
        t = Transaction(100, "Ancienne description", "dépense", 1, date(2026, 1, 10))
        t_id = transaction_service.add_transaction(t)
        
        t_updated = Transaction(100, "Nouvelle description", "dépense", 1, date(2026, 1, 10))
        transaction_service.update_transaction(t_id, t_updated)
        
        retrieved = transaction_service.get_transaction_by_id(t_id)
        assert retrieved.description == "Nouvelle description"
    
    def test_update_transaction_category(self, transaction_service):
        """Test: changement de catégorie"""
        t = Transaction(100, "Transaction", "dépense", 1, date(2026, 1, 10))
        t_id = transaction_service.add_transaction(t)
        
        t_updated = Transaction(100, "Transaction", "dépense", 2, date(2026, 1, 10))
        transaction_service.update_transaction(t_id, t_updated)
        
        retrieved = transaction_service.get_transaction_by_id(t_id)
        assert retrieved.category_id == 2
    
    def test_update_transaction_type(self, transaction_service):
        """Test: changement de type (dépense vers revenu)"""
        t = Transaction(100, "Transaction", "dépense", 1, date(2026, 1, 10))
        t_id = transaction_service.add_transaction(t)
        
        t_updated = Transaction(100, "Transaction", "revenu", 1, date(2026, 1, 10))
        transaction_service.update_transaction(t_id, t_updated)
        
        retrieved = transaction_service.get_transaction_by_id(t_id)
        assert retrieved.type == "revenu"
    
    def test_update_transaction_date(self, transaction_service):
        """Test: modification de la date"""
        t = Transaction(100, "Transaction", "dépense", 1, date(2026, 1, 10))
        t_id = transaction_service.add_transaction(t)
        
        t_updated = Transaction(100, "Transaction", "dépense", 1, date(2026, 1, 20))
        transaction_service.update_transaction(t_id, t_updated)
        
        retrieved = transaction_service.get_transaction_by_id(t_id)
        assert retrieved.date == date(2026, 1, 20)
    
    def test_update_nonexistent_transaction(self, transaction_service):
        """Test: mise à jour d'une transaction inexistante"""
        t = Transaction(100, "Test", "dépense", 1, date(2026, 1, 10))
        success = transaction_service.update_transaction(9999, t)
        
        assert success is False
    
    def test_delete_transaction(self, transaction_service):
        """Test: suppression d'une transaction"""
        t = Transaction(100, "À supprimer", "dépense", 1, date(2026, 1, 10))
        t_id = transaction_service.add_transaction(t)
        
        success = transaction_service.delete_transaction(t_id)
        
        assert success is True
        assert transaction_service.get_transaction_by_id(t_id) is None
    
    def test_delete_nonexistent_transaction(self, transaction_service):
        """Test: suppression d'une transaction inexistante"""
        success = transaction_service.delete_transaction(9999)
        assert success is False
    
    def test_delete_affects_total(self, transaction_service):
        """Test: la suppression affecte le total des dépenses"""
        # Ajouter des transactions
        t1 = Transaction(100, "Transaction 1", "dépense", 1, date(2026, 1, 10))
        t2 = Transaction(50, "Transaction 2", "dépense", 1, date(2026, 1, 15))
        
        t1_id = transaction_service.add_transaction(t1)
        transaction_service.add_transaction(t2)
        
        # Total initial
        total_before = transaction_service.get_total_by_category(
            1, date(2026, 1, 1), date(2026, 1, 31), 'dépense'
        )
        assert total_before == 150
        
        # Supprimer une transaction
        transaction_service.delete_transaction(t1_id)
        
        # Vérifier le nouveau total
        total_after = transaction_service.get_total_by_category(
            1, date(2026, 1, 1), date(2026, 1, 31), 'dépense'
        )
        assert total_after == 50
    
    def test_update_affects_total(self, transaction_service):
        """Test: la modification affecte le total des dépenses"""
        # Ajouter une transaction
        t = Transaction(100, "Transaction", "dépense", 1, date(2026, 1, 10))
        t_id = transaction_service.add_transaction(t)
        
        # Total initial
        total_before = transaction_service.get_total_by_category(
            1, date(2026, 1, 1), date(2026, 1, 31), 'dépense'
        )
        assert total_before >= 100
        
        # Modifier le montant
        t_updated = Transaction(200, "Transaction", "dépense", 1, date(2026, 1, 10))
        transaction_service.update_transaction(t_id, t_updated)
        
        # Vérifier le nouveau total
        total_after = transaction_service.get_total_by_category(
            1, date(2026, 1, 1), date(2026, 1, 31), 'dépense'
        )
        assert total_after >= 200
    
    def test_update_multiple_fields(self, transaction_service):
        """Test: modification de plusieurs champs simultanément"""
        t = Transaction(100, "Original", "dépense", 1, date(2026, 1, 10))
        t_id = transaction_service.add_transaction(t)
        
        t_updated = Transaction(250, "Complètement modifié", "revenu", 3, date(2026, 1, 25))
        transaction_service.update_transaction(t_id, t_updated)
        
        retrieved = transaction_service.get_transaction_by_id(t_id)
        assert retrieved.amount == 250
        assert retrieved.description == "Complètement modifié"
        assert retrieved.type == "revenu"
        assert retrieved.category_id == 3
        assert retrieved.date == date(2026, 1, 25)
    
    def test_update_preserves_id(self, transaction_service):
        """Test: la mise à jour préserve l'ID de la transaction"""
        t = Transaction(100, "Original", "dépense", 1, date(2026, 1, 10))
        t_id = transaction_service.add_transaction(t)
        
        t_updated = Transaction(150, "Modifié", "dépense", 1, date(2026, 1, 10))
        transaction_service.update_transaction(t_id, t_updated)
        
        retrieved = transaction_service.get_transaction_by_id(t_id)
        assert retrieved.id == t_id
