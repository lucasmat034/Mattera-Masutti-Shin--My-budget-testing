# src/services/budget_service.py

from datetime import date
from typing import List, Optional, Dict
from src.database.db_manager import DatabaseManager
from src.models.budget import Budget
from src.services.transaction_service import TransactionService

class BudgetService:
    """Service pour gérer les budgets"""
    
    def __init__(self, db_manager: DatabaseManager, transaction_service: TransactionService):
        self.db = db_manager
        self.transaction_service = transaction_service
    
    def create_budget(self, budget: Budget) -> int:
        """Crée un nouveau budget et retourne son ID"""
        query = """
        INSERT INTO budgets (category_id, amount, period_start, period_end)
        VALUES (?, ?, ?, ?)
        """
        params = (
            budget.category_id,
            budget.amount,
            budget.period_start.isoformat(),
            budget.period_end.isoformat()
        )
        return self.db.execute_update(query, params)
    
    def get_budget_status(self, category_id: int, period_start: date, period_end: date) -> Optional[Dict]:
        """Récupère le statut d'un budget (montant, dépensé, restant, %)"""
        # Récupérer le budget
        query = """
        SELECT * FROM budgets
        WHERE category_id = ?
        AND period_start = ?
        AND period_end = ?
        """
        params = (category_id, period_start.isoformat(), period_end.isoformat())
        results = self.db.execute_query(query, params)
        
        if not results:
            return None
        
        budget_data = results[0]
        budget_amount = budget_data['amount']
        
        # Calculer le total dépensé
        spent = self.transaction_service.get_total_by_category(
            category_id, period_start, period_end, 'dépense'
        )
        
        # Calculer les métriques
        remaining = budget_amount - spent
        percentage = (spent / budget_amount * 100) if budget_amount > 0 else 0
        is_exceeded = spent > budget_amount
        
        return {
            'budget_id': budget_data['id'],
            'category_id': category_id,
            'budget_amount': budget_amount,
            'spent': spent,
            'remaining': remaining,
            'percentage': round(percentage, 1),
            'is_exceeded': is_exceeded
        }
    
    def list_budgets(self, category_id: Optional[int] = None) -> List[Budget]:
        """Liste tous les budgets, avec filtre optionnel par catégorie"""
        query = "SELECT * FROM budgets"
        params = []
        
        if category_id:
            query += " WHERE category_id = ?"
            params.append(category_id)
        
        query += " ORDER BY period_start DESC"
        
        results = self.db.execute_query(query, tuple(params))
        
        return [
            Budget(
                id=row['id'],
                category_id=row['category_id'],
                amount=row['amount'],
                period_start=date.fromisoformat(row['period_start']),
                period_end=date.fromisoformat(row['period_end'])
            )
            for row in results
        ]
