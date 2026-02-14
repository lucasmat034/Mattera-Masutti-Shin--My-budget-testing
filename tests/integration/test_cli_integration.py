# tests/integration/test_cli_integration.py

import pytest
import json
from click.testing import CliRunner
from datetime import date
from src.cli.main import cli, db

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
    
    def test_update_transaction_command(self, runner):
        """Test: modification d'une transaction via CLI"""
        runner.invoke(cli, ['reset', '--yes'])
        runner.invoke(cli, ['add', '10', 'Test', 'alimentation', '2026-01-10'])

        row = db.execute_query(
            "SELECT id FROM transactions ORDER BY id DESC LIMIT 1"
        )[0]
        t_id = row['id']

        result = runner.invoke(
            cli,
            ['update', str(t_id), '--amount', '25', '--description', 'Modifie']
        )
        assert result.exit_code == 0

        updated = db.execute_query(
            "SELECT amount, description FROM transactions WHERE id = ?",
            (t_id,)
        )[0]
        assert updated['amount'] == 25
        assert updated['description'] == 'Modifie'

    def test_delete_transaction_command(self, runner):
        """Test: suppression d'une transaction via CLI"""
        runner.invoke(cli, ['reset', '--yes'])
        runner.invoke(cli, ['add', '10', 'Test', 'alimentation', '2026-01-10'])

        row = db.execute_query(
            "SELECT id FROM transactions ORDER BY id DESC LIMIT 1"
        )[0]
        t_id = row['id']

        result = runner.invoke(cli, ['delete', str(t_id), '--yes'])
        assert result.exit_code == 0
        assert db.execute_query("SELECT * FROM transactions WHERE id = ?", (t_id,)) == []

    def test_export_command_csv(self, runner, tmp_path):
        """Test: export des transactions en CSV via CLI"""
        runner.invoke(cli, ['reset', '--yes'])
        runner.invoke(cli, ['add', '10', 'Test', 'alimentation', '2026-01-10'])

        output = tmp_path / "export.csv"
        result = runner.invoke(cli, ['export', '--format', 'csv', '--output', str(output)])

        assert result.exit_code == 0
        assert output.exists()
        with open(output, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
            assert len(lines) >= 2  # header + at least one row

    def test_export_budget_command_json(self, runner, tmp_path):
        """Test: export du resume budget en JSON via CLI"""
        runner.invoke(cli, ['reset', '--yes'])
        runner.invoke(cli, ['budget', 'alimentation', '100', '2026-01-01', '2026-01-31'])
        runner.invoke(cli, ['add', '10', 'Test', 'alimentation', '2026-01-10'])

        output = tmp_path / "budget.json"
        result = runner.invoke(
            cli,
            ['export-budget', 'alimentation', '2026-01-01', '2026-01-31', '-o', str(output)]
        )

        assert result.exit_code == 0
        assert output.exists()
        with open(output, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert 'budget' in data
            assert 'transactions' in data

    def test_reset_command(self, runner):
        """Test: reinitialisation des donnees via CLI"""
        # Ajouter des donnees
        runner.invoke(cli, ['add', '10', 'Test', 'alimentation', '2026-01-10'])
        runner.invoke(cli, ['budget', 'alimentation', '100', '2026-01-01', '2026-01-31'])

        # Reinitialiser
        result = runner.invoke(cli, ['reset', '--yes'])
        assert result.exit_code == 0

        # Verifier la base
        assert len(db.execute_query("SELECT * FROM transactions")) == 0
        assert len(db.execute_query("SELECT * FROM budgets")) == 0
        assert len(db.execute_query("SELECT * FROM categories")) >= 6

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
