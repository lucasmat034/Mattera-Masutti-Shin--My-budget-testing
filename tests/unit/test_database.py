import pytest
from datetime import date
from src.database.db_manager import DatabaseManager

class TestDatabaseManager:
    """Tests du gestionnaire de base de données"""
    
    def test_create_tables(self):
        """Test: création des tables"""
        db = DatabaseManager(":memory:")
        
        # Vérifier que les tables existent
        tables = db.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        table_names = [t['name'] for t in tables]
        
        assert 'categories' in table_names
        assert 'transactions' in table_names
        assert 'budgets' in table_names
        
        db.close()
    
    def test_default_categories(self):
        """Test: création des catégories par défaut"""
        db = DatabaseManager(":memory:")
        
        categories = db.execute_query("SELECT * FROM categories")
        category_names = [c['name'] for c in categories]
        
        assert 'alimentation' in category_names
        assert 'logement' in category_names
        assert 'loisirs' in category_names
        assert 'transports' in category_names
        assert 'santé' in category_names
        assert 'autres' in category_names
        
        db.close()
    
    def test_execute_query(self):
        """Test: exécution d'une requête SELECT"""
        db = DatabaseManager(":memory:")
        
        results = db.execute_query(
            "SELECT * FROM categories WHERE name = ?",
            ('alimentation',)
        )
        
        assert len(results) == 1
        assert results[0]['name'] == 'alimentation'
        
        db.close()
    
    def test_execute_update_insert(self):
        """Test: insertion de données"""
        db = DatabaseManager(":memory:")
        
        transaction_id = db.execute_update(
            "INSERT INTO transactions (amount, description, type, category_id, date) VALUES (?, ?, ?, ?, ?)",
            (50.0, "Test", "dépense", 1, "2026-01-10")
        )
        
        assert transaction_id > 0
        
        # Vérifier l'insertion
        result = db.execute_query(
            "SELECT * FROM transactions WHERE id = ?",
            (transaction_id,)
        )
        assert len(result) == 1
        assert result[0]['amount'] == 50.0
        
        db.close()
    
    def test_execute_update_delete(self):
        """Test: suppression de données"""
        db = DatabaseManager(":memory:")
        
        # Insérer une transaction
        t_id = db.execute_update(
            "INSERT INTO transactions (amount, description, type, category_id, date) VALUES (?, ?, ?, ?, ?)",
            (30.0, "Test", "dépense", 1, "2026-01-10")
        )
        
        # Supprimer la transaction
        rows_affected = db.execute_update(
            "DELETE FROM transactions WHERE id = ?",
            (t_id,)
        )
        
        assert rows_affected == 1
        
        # Vérifier qu'elle n'existe plus
        result = db.execute_query(
            "SELECT * FROM transactions WHERE id = ?",
            (t_id,)
        )
        assert len(result) == 0
        
        db.close()
    
    def test_reset_data_clears_transactions_and_budgets(self):
        """Test: reset data"""
        db = DatabaseManager(":memory:")

        # Insert a transaction and a budget
        db.execute_update(
            "INSERT INTO transactions (amount, description, type, category_id, date) VALUES (?, ?, ?, ?, ?)",
            (25.0, "Test", "dépense", 1, "2026-01-10")
        )
        db.execute_update(
            "INSERT INTO budgets (category_id, amount, period_start, period_end) VALUES (?, ?, ?, ?)",
            (1, 200.0, "2026-01-01", "2026-01-31")
        )

        assert len(db.execute_query("SELECT * FROM transactions")) == 1
        assert len(db.execute_query("SELECT * FROM budgets")) == 1

        # Reset
        db.reset_data()

        # Transactions and budgets cleared, categories preserved
        assert len(db.execute_query("SELECT * FROM transactions")) == 0
        assert len(db.execute_query("SELECT * FROM budgets")) == 0
        assert len(db.execute_query("SELECT * FROM categories")) == 6

        db.close()

    def test_context_manager(self):
        """Test: utilisation comme context manager"""
        with DatabaseManager(":memory:") as db:
            categories = db.execute_query("SELECT * FROM categories")
            assert len(categories) > 0
        
        # La connexion doit être fermée
        # (Pas de méthode simple pour tester cela sans lever une exception)
