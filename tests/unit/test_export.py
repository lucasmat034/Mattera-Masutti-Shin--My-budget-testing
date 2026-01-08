# tests/unit/test_export.py

import pytest
import json
import csv
from datetime import date
from pathlib import Path
from src.models.transaction import Transaction
from src.services.export_service import ExportService

class TestExportService:
    """Tests du service d'export"""
    
    @pytest.fixture
    def export_service(self, db_manager, transaction_service):
        """Fixture pour le service d'export"""
        return ExportService(db_manager, transaction_service)
    
    @pytest.fixture
    def sample_transactions(self, transaction_service):
        """Crée des transactions de test"""
        t1 = Transaction(100, "Courses 1", "dépense", 1, date(2026, 1, 5))
        t2 = Transaction(50, "Courses 2", "dépense", 1, date(2026, 1, 10))
        t3 = Transaction(75, "Essence", "dépense", 4, date(2026, 1, 12))
        
        transaction_service.add_transaction(t1)
        transaction_service.add_transaction(t2)
        transaction_service.add_transaction(t3)
        
        return 3
    
    def test_export_to_csv_all_transactions(self, export_service, sample_transactions, tmp_path):
        """Test: export de toutes les transactions en CSV"""
        filepath = tmp_path / "transactions.csv"
        
        count = export_service.export_transactions_to_csv(str(filepath))
        
        assert count == sample_transactions
        assert filepath.exists()
        
        # Vérifier le contenu du CSV
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == sample_transactions
            assert rows[0]['description'] in ['Courses 1', 'Courses 2', 'Essence']
    
    def test_export_to_csv_filtered_by_category(self, export_service, sample_transactions, tmp_path):
        """Test: export filtré par catégorie en CSV"""
        filepath = tmp_path / "alimentation.csv"
        
        count = export_service.export_transactions_to_csv(str(filepath), category_id=1)
        
        assert count == 2  # Seulement alimentation
        
        # Vérifier le contenu
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert all(row['category_id'] == '1' for row in rows)
    
    def test_export_to_csv_filtered_by_date(self, export_service, sample_transactions, tmp_path):
        """Test: export filtré par date en CSV"""
        filepath = tmp_path / "january_first_week.csv"
        
        count = export_service.export_transactions_to_csv(
            str(filepath),
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 7)
        )
        
        assert count == 1  # Seulement la première transaction
    
    def test_export_to_json_all_transactions(self, export_service, sample_transactions, tmp_path):
        """Test: export de toutes les transactions en JSON"""
        filepath = tmp_path / "transactions.json"
        
        count = export_service.export_transactions_to_json(str(filepath))
        
        assert count == sample_transactions
        assert filepath.exists()
        
        # Vérifier le contenu du JSON
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert data['count'] == sample_transactions
            assert len(data['transactions']) == sample_transactions
            assert 'export_date' in data
    
    def test_export_to_json_pretty_format(self, export_service, sample_transactions, tmp_path):
        """Test: export JSON avec formatage"""
        filepath = tmp_path / "pretty.json"
        
        export_service.export_transactions_to_json(str(filepath), pretty=True)
        
        # Vérifier que le fichier est indenté (contient des retours à la ligne)
        with open(filepath, 'r') as f:
            content = f.read()
            assert '\n' in content
            assert '  ' in content  # Indentation
    
    def test_export_to_json_compact_format(self, export_service, sample_transactions, tmp_path):
        """Test: export JSON compact"""
        filepath_pretty = tmp_path / "pretty.json"
        filepath_compact = tmp_path / "compact.json"
        
        export_service.export_transactions_to_json(str(filepath_pretty), pretty=True)
        export_service.export_transactions_to_json(str(filepath_compact), pretty=False)
        
        # Le fichier compact doit être plus petit
        assert filepath_compact.stat().st_size < filepath_pretty.stat().st_size
    
    def test_export_budget_summary(self, export_service, transaction_service, tmp_path):
        """Test: export du résumé de budget"""
        from src.models.budget import Budget
        from src.services.budget_service import BudgetService
        
        # Créer un budget
        budget_service = BudgetService(export_service.db, transaction_service)
        b = Budget(1, 300, date(2026, 1, 1), date(2026, 1, 31))
        budget_service.create_budget(b)
        
        # Ajouter des transactions
        t1 = Transaction(100, "Test 1", "dépense", 1, date(2026, 1, 10))
        t2 = Transaction(50, "Test 2", "dépense", 1, date(2026, 1, 15))
        transaction_service.add_transaction(t1)
        transaction_service.add_transaction(t2)
        
        # Exporter
        filepath = tmp_path / "budget_summary.json"
        success = export_service.export_budget_summary_to_json(
            str(filepath),
            category_id=1,
            period_start=date(2026, 1, 1),
            period_end=date(2026, 1, 31)
        )
        
        assert success is True
        assert filepath.exists()
        
        # Vérifier le contenu
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert 'budget' in data
            assert 'transactions' in data
            assert data['category'] == 'alimentation'
            assert data['budget']['budget_amount'] == 300
    
    def test_export_creates_directories(self, export_service, sample_transactions, tmp_path):
        """Test: l'export crée les dossiers nécessaires"""
        filepath = tmp_path / "nested" / "folder" / "export.csv"
        
        export_service.export_transactions_to_csv(str(filepath))
        
        assert filepath.exists()
        assert filepath.parent.exists()
