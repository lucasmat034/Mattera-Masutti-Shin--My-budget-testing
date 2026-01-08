# src/services/transaction_service.py

from datetime import date, datetime
from typing import List, Optional, Dict
from src.database.db_manager import DatabaseManager
from src.models.transaction import Transaction

class TransactionService:
    """Service pour gérer les transactions"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def add_transaction(self, transaction: Transaction) -> int:
        """Ajoute une nouvelle transaction et retourne son ID"""
        query = """
        INSERT INTO transactions (amount, description, type, category_id, date)
        VALUES (?, ?, ?, ?, ?)
        """
        params = (
            transaction.amount,
            transaction.description,
            transaction.type,
            transaction.category_id,
            transaction.date.isoformat()
        )
        return self.db.execute_update(query, params)
    
    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Récupère une transaction par son ID"""
        query = "SELECT * FROM transactions WHERE id = ?"
        results = self.db.execute_query(query, (transaction_id,))
        
        if not results:
            return None
        
        row = results[0]
        return Transaction(
            id=row['id'],
            amount=row['amount'],
            description=row['description'],
            type=row['type'],
            category_id=row['category_id'],
            date=datetime.strptime(row['date'], '%Y-%m-%d').date()
        )
    
    def list_transactions(
        self, 
        category_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        transaction_type: Optional[str] = None
    ) -> List[Transaction]:
        """Liste les transactions avec filtres optionnels"""
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []
        
        if category_id:
            query += " AND category_id = ?"
            params.append(category_id)
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date.isoformat())
        
        if transaction_type:
            query += " AND type = ?"
            params.append(transaction_type)
        
        query += " ORDER BY date DESC"
        
        results = self.db.execute_query(query, tuple(params))
        
        return [
            Transaction(
                id=row['id'],
                amount=row['amount'],
                description=row['description'],
                type=row['type'],
                category_id=row['category_id'],
                date=datetime.strptime(row['date'], '%Y-%m-%d').date()
            )
            for row in results
        ]
    
    def get_total_by_category(
        self, 
        category_id: int, 
        start_date: date, 
        end_date: date,
        transaction_type: str = 'dépense'
    ) -> float:
        """Calcule le total des transactions pour une catégorie sur une période"""
        query = """
        SELECT COALESCE(SUM(amount), 0) as total
        FROM transactions
        WHERE category_id = ?
        AND date >= ?
        AND date <= ?
        AND type = ?
        """
        params = (category_id, start_date.isoformat(), end_date.isoformat(), transaction_type)
        result = self.db.execute_query(query, params)
        return result[0]['total'] if result else 0.0
    
    def update_transaction(self, transaction_id: int, transaction: Transaction) -> bool:
        """Met à jour une transaction existante"""
        query = """
        UPDATE transactions
        SET amount = ?, description = ?, type = ?, category_id = ?, date = ?
        WHERE id = ?
        """
        params = (
            transaction.amount,
            transaction.description,
            transaction.type,
            transaction.category_id,
            transaction.date.isoformat(),
            transaction_id
        )
        rows_affected = self.db.execute_update(query, params)
        return rows_affected > 0
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """Supprime une transaction"""
        query = "DELETE FROM transactions WHERE id = ?"
        rows_affected = self.db.execute_update(query, (transaction_id,))
        return rows_affected > 0
