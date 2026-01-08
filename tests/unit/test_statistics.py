# tests/unit/test_statistics.py

import pytest
from datetime import date, timedelta
from src.models.transaction import Transaction
from src.services.statistics_service import StatisticsService

class TestStatisticsService:
    """Tests du service de statistiques"""
    
    @pytest.fixture
    def statistics_service(self, db_manager, transaction_service):
        """Fixture pour le service de statistiques"""
        return StatisticsService(db_manager, transaction_service)
    
    def test_monthly_summary(self, statistics_service, transaction_service):
        """Test: génération du résumé mensuel"""
        # Ajouter des transactions pour janvier 2026
        t1 = Transaction(100, "Courses", "dépense", 1, date(2026, 1, 5))
        t2 = Transaction(500, "Salaire", "revenu", 6, date(2026, 1, 1))
        t3 = Transaction(50, "Restaurant", "dépense", 1, date(2026, 1, 15))
        
        transaction_service.add_transaction(t1)
        transaction_service.add_transaction(t2)
        transaction_service.add_transaction(t3)
        
        # Générer le résumé
        summary = statistics_service.get_monthly_summary(2026, 1)
        
        assert summary['total_revenus'] >= 500
        assert summary['total_depenses'] >= 150
        assert summary['balance'] >= 350
        assert summary['transactions_count'] >= 3
    
    def test_category_trend(self, statistics_service, transaction_service):
        """Test: tendance d'une catégorie sur plusieurs mois"""
        # Ajouter des transactions sur 3 mois différents
        t1 = Transaction(100, "Janvier", "dépense", 1, date(2026, 1, 10))
        t2 = Transaction(150, "Décembre", "dépense", 1, date(2025, 12, 15))
        t3 = Transaction(120, "Novembre", "dépense", 1, date(2025, 11, 20))
        
        transaction_service.add_transaction(t1)
        transaction_service.add_transaction(t2)
        transaction_service.add_transaction(t3)
        
        # Obtenir la tendance
        trends = statistics_service.get_category_trend(category_id=1, months=3)
        
        assert len(trends) == 3
        assert all('year' in t and 'month' in t and 'total' in t for t in trends)
    
    def test_average_spending(self, statistics_service, transaction_service):
        """Test: calcul de la moyenne des dépenses"""
        # Ajouter des transactions régulières
        t1 = Transaction(100, "Mois 1", "dépense", 1, date(2026, 1, 10))
        t2 = Transaction(150, "Mois 2", "dépense", 1, date(2025, 12, 15))
        t3 = Transaction(120, "Mois 3", "dépense", 1, date(2025, 11, 20))
        
        transaction_service.add_transaction(t1)
        transaction_service.add_transaction(t2)
        transaction_service.add_transaction(t3)
        
        average = statistics_service.get_average_spending_by_category(category_id=1, months=3)
        
        # Moyenne devrait être autour de (100+150+120)/3 = 123.33
        assert average > 0
        assert isinstance(average, float)
    
    def test_top_expenses(self, statistics_service, transaction_service):
        """Test: récupération des plus grandes dépenses"""
        today = date.today()
        
        # Ajouter plusieurs transactions
        t1 = Transaction(500, "Grande dépense", "dépense", 1, today)
        t2 = Transaction(50, "Petite dépense", "dépense", 1, today - timedelta(days=1))
        t3 = Transaction(200, "Moyenne dépense", "dépense", 2, today - timedelta(days=5))
        
        transaction_service.add_transaction(t1)
        transaction_service.add_transaction(t2)
        transaction_service.add_transaction(t3)
        
        # Récupérer le top 3
        top = statistics_service.get_top_expenses(limit=3, days=30)
        
        assert len(top) >= 3
        # Doit être trié par montant décroissant
        assert top[0]['amount'] >= top[1]['amount']
        assert top[1]['amount'] >= top[2]['amount']
    
    def test_spending_by_day_of_week(self, statistics_service, transaction_service):
        """Test: analyse par jour de la semaine"""
        # Ajouter des transactions sur différents jours
        today = date.today()
        
        for i in range(7):
            t = Transaction(100, f"Jour {i}", "dépense", 1, today - timedelta(days=i))
            transaction_service.add_transaction(t)
        
        by_weekday = statistics_service.get_spending_by_day_of_week(category_id=1, months=1)
        
        # Devrait retourner 7 jours
        assert len(by_weekday) == 7
        assert 'Lundi' in by_weekday or 'Mardi' in by_weekday  # Au moins un jour présent
    
    def test_predict_end_of_month(self, statistics_service, transaction_service):
        """Test: prédiction de fin de mois"""
        # Ajouter des transactions ce mois-ci
        today = date.today()
        start_of_month = date(today.year, today.month, 1)
        
        for i in range(5):
            t = Transaction(30, f"Transaction {i}", "dépense", 1, start_of_month + timedelta(days=i))
            transaction_service.add_transaction(t)
        
        prediction = statistics_service.predict_end_of_month_spending(category_id=1)
        
        assert 'current_spending' in prediction
        assert 'daily_average' in prediction
        assert 'projected_total' in prediction
        assert prediction['current_spending'] >= 150  # 5 * 30
        assert prediction['projected_total'] > prediction['current_spending']
    
    def test_monthly_summary_by_category(self, statistics_service, transaction_service):
        """Test: résumé mensuel avec détail par catégorie"""
        # Ajouter des transactions dans différentes catégories
        t1 = Transaction(100, "Alimentation", "dépense", 1, date(2026, 1, 10))
        t2 = Transaction(200, "Loisirs", "dépense", 3, date(2026, 1, 15))
        
        transaction_service.add_transaction(t1)
        transaction_service.add_transaction(t2)
        
        summary = statistics_service.get_monthly_summary(2026, 1)
        
        assert 'by_category' in summary
        assert len(summary['by_category']) >= 2
    
    def test_empty_period_statistics(self, statistics_service):
        """Test: statistiques sur une période vide"""
        # Résumé d'un mois sans transactions
        summary = statistics_service.get_monthly_summary(2020, 1)
        
        assert summary['total_revenus'] == 0
        assert summary['total_depenses'] == 0
        assert summary['balance'] == 0
        assert summary['transactions_count'] == 0
