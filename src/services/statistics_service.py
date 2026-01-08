# src/services/statistics_service.py

from datetime import date, timedelta
from typing import Dict, List, Optional
from src.database.db_manager import DatabaseManager
from src.services.transaction_service import TransactionService

class StatisticsService:
    """Service pour les statistiques avancées sur les transactions"""
    
    def __init__(self, db_manager: DatabaseManager, transaction_service: TransactionService):
        self.db = db_manager
        self.transaction_service = transaction_service
    
    def get_monthly_summary(self, year: int, month: int) -> Dict:
        """
        Génère un résumé mensuel des finances
        
        Returns:
            Dictionnaire avec total revenus, dépenses, balance, et par catégorie
        """
        # Calculer les dates de début et fin du mois
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        # Récupérer toutes les transactions du mois
        transactions = self.transaction_service.list_transactions(
            start_date=start_date,
            end_date=end_date
        )
        
        # Calculer les totaux
        total_revenus = sum(t.amount for t in transactions if t.type == 'revenu')
        total_depenses = sum(t.amount for t in transactions if t.type == 'dépense')
        balance = total_revenus - total_depenses
        
        # Regrouper par catégorie
        by_category = {}
        for t in transactions:
            if t.category_id not in by_category:
                # Récupérer le nom de la catégorie
                cat_data = self.db.execute_query(
                    "SELECT name FROM categories WHERE id = ?",
                    (t.category_id,)
                )
                cat_name = cat_data[0]['name'] if cat_data else f"Category {t.category_id}"
                by_category[t.category_id] = {
                    'name': cat_name,
                    'revenus': 0,
                    'depenses': 0
                }
            
            if t.type == 'revenu':
                by_category[t.category_id]['revenus'] += t.amount
            else:
                by_category[t.category_id]['depenses'] += t.amount
        
        return {
            'period': {
                'year': year,
                'month': month,
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'total_revenus': total_revenus,
            'total_depenses': total_depenses,
            'balance': balance,
            'transactions_count': len(transactions),
            'by_category': list(by_category.values())
        }
    
    def get_category_trend(self, category_id: int, months: int = 6) -> List[Dict]:
        """
        Analyse l'évolution des dépenses d'une catégorie sur plusieurs mois
        
        Args:
            category_id: ID de la catégorie
            months: Nombre de mois à analyser (défaut: 6)
            
        Returns:
            Liste des totaux par mois
        """
        today = date.today()
        trends = []
        
        for i in range(months):
            # Calculer le mois
            month = today.month - i
            year = today.year
            
            while month <= 0:
                month += 12
                year -= 1
            
            # Dates du mois
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = date(year, month + 1, 1) - timedelta(days=1)
            
            # Total pour ce mois
            total = self.transaction_service.get_total_by_category(
                category_id, start_date, end_date, 'dépense'
            )
            
            trends.append({
                'year': year,
                'month': month,
                'total': total
            })
        
        return list(reversed(trends))
    
    def get_average_spending_by_category(self, category_id: int, months: int = 3) -> float:
        """Calcule la moyenne des dépenses mensuelles pour une catégorie"""
        trends = self.get_category_trend(category_id, months)
        
        if not trends:
            return 0.0
        
        total = sum(t['total'] for t in trends)
        return round(total / len(trends), 2)
    
    def get_top_expenses(self, limit: int = 10, days: int = 30) -> List[Dict]:
        """
        Récupère les plus grandes dépenses récentes
        
        Args:
            limit: Nombre maximum de résultats
            days: Période en jours (défaut: 30 derniers jours)
            
        Returns:
            Liste des transactions triées par montant décroissant
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        transactions = self.transaction_service.list_transactions(
            start_date=start_date,
            end_date=end_date,
            transaction_type='dépense'
        )
        
        # Trier par montant décroissant
        sorted_transactions = sorted(
            transactions,
            key=lambda t: t.amount,
            reverse=True
        )[:limit]
        
        # Convertir en dict avec nom de catégorie
        result = []
        for t in sorted_transactions:
            cat_data = self.db.execute_query(
                "SELECT name FROM categories WHERE id = ?",
                (t.category_id,)
            )
            cat_name = cat_data[0]['name'] if cat_data else "Unknown"
            
            result.append({
                'id': t.id,
                'amount': t.amount,
                'description': t.description,
                'category': cat_name,
                'date': t.date.isoformat()
            })
        
        return result
    
    def get_spending_by_day_of_week(self, category_id: Optional[int] = None, months: int = 3) -> Dict:
        """
        Analyse les dépenses par jour de la semaine
        
        Returns:
            Dictionnaire avec total par jour (0=lundi, 6=dimanche)
        """
        # Calculer la période
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)
        
        transactions = self.transaction_service.list_transactions(
            category_id=category_id,
            start_date=start_date,
            end_date=end_date,
            transaction_type='dépense'
        )
        
        # Grouper par jour de la semaine
        by_weekday = {i: 0 for i in range(7)}
        
        for t in transactions:
            weekday = t.date.weekday()
            by_weekday[weekday] += t.amount
        
        weekday_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        
        return {
            weekday_names[day]: round(total, 2)
            for day, total in by_weekday.items()
        }
    
    def predict_end_of_month_spending(self, category_id: int) -> Dict:
        """
        Prédit les dépenses en fin de mois basé sur la tendance actuelle
        
        Returns:
            Dictionnaire avec dépenses actuelles, moyenne quotidienne, et projection
        """
        today = date.today()
        start_of_month = date(today.year, today.month, 1)
        
        # Jours écoulés dans le mois
        days_elapsed = (today - start_of_month).days + 1
        
        # Total actuel
        current_spending = self.transaction_service.get_total_by_category(
            category_id, start_of_month, today, 'dépense'
        )
        
        # Moyenne par jour
        daily_average = current_spending / days_elapsed if days_elapsed > 0 else 0
        
        # Nombre de jours dans le mois
        if today.month == 12:
            end_of_month = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_of_month = date(today.year, today.month + 1, 1) - timedelta(days=1)
        
        days_in_month = end_of_month.day
        
        # Projection
        projected_spending = daily_average * days_in_month
        
        return {
            'current_spending': round(current_spending, 2),
            'days_elapsed': days_elapsed,
            'daily_average': round(daily_average, 2),
            'days_in_month': days_in_month,
            'projected_total': round(projected_spending, 2)
        }
