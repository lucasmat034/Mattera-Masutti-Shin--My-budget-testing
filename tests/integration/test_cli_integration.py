# tests/integration/test_cli_integration.py

import pytest
from click.testing import CliRunner
from datetime import date
from src.cli.main import cli
from src.database.db_manager import DatabaseManager

class TestCLIIntegration:
    """Tests d'intégration de l'interface CLI"""
    
    @pytest.fixture
    def runner(self):
        """Fixture pour le CLI runner"""
        return CliRunner()
    
    def test_add_transaction_command(self, runner):
        """Test: commande d'ajout de transaction"""
        result = runner.invoke(cli, ['add', '50.00', 'Test transaction', 'alimentation', '2026-01-10'])
        
        assert result.exit_code == 0
        assert '✅' in result.output or 'Transaction ajoutée' in result.output.lower()
    
    def test_list_transactions_command(self, runner):
        """Test: commande de listage"""
        # Ajouter d'abord une transaction
        runner.invoke(cli, ['add', '30.00', 'Test', 'alimentation', '2026-01-05'])
        
        # Lister
        result = runner.invoke(cli, ['list'])
        
        assert result.exit_code == 0
    
    def test_budget_command(self, runner):
        """Test: création d'un budget"""
        result = runner.invoke(cli, [
            'budget',
            'alimentation',
            '300',
            '2026-01-01',
            '2026-01-31'
        ])
        
        assert result.exit_code == 0
        assert '✅' in result.output or 'budget' in result.output.lower()
    
    def test_status_command(self, runner):
        """Test: affichage du statut"""
        # Créer un budget
        runner.invoke(cli, ['budget', 'alimentation', '300', '2026-01-01', '2026-01-31'])
        
        # Ajouter une dépense
        runner.invoke(cli, ['add', '100', 'Courses', 'alimentation', '2026-01-10'])
        
        # Vérifier le statut
        result = runner.invoke(cli, ['status', 'alimentation', '2026-01-01', '2026-01-31'])
        
        assert result.exit_code == 0
        assert 'Budget' in result.output or 'budget' in result.output
    
    def test_invalid_category(self, runner):
        """Test: tentative avec catégorie invalide"""
        result = runner.invoke(cli, ['add', '50', 'Test', 'categorie_inexistante', '2026-01-10'])
        
        assert result.exit_code == 0
        assert 'inconnue' in result.output or 'Catégorie' in result.output
    
    def test_full_workflow(self, runner):
        """Test: workflow complet"""
        # 1. Créer un budget
        result1 = runner.invoke(cli, ['budget', 'loisirs', '200', '2026-01-01', '2026-01-31'])
        assert result1.exit_code == 0
        
        # 2. Ajouter des transactions
        result2 = runner.invoke(cli, ['add', '50', 'Cinéma', 'loisirs', '2026-01-05'])
        assert result2.exit_code == 0
        
        result3 = runner.invoke(cli, ['add', '80', 'Concert', 'loisirs', '2026-01-15'])
        assert result3.exit_code == 0
        
        # 3. Vérifier le statut
        result4 = runner.invoke(cli, ['status', 'loisirs', '2026-01-01', '2026-01-31'])
        assert result4.exit_code == 0
        
        # 4. Lister les transactions
        result5 = runner.invoke(cli, ['list', '--category', 'loisirs'])
        assert result5.exit_code == 0
