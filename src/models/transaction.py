# src/models/transaction.py

from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Transaction:
    """Modèle représentant une transaction financière"""
    amount: float
    description: str
    type: str  # 'revenu' ou 'dépense'
    category_id: int
    date: date
    id: Optional[int] = None
    
    def __post_init__(self):
        """Validation des données"""
        if self.amount <= 0:
            raise ValueError("Le montant doit être positif")
        
        if self.type not in ['revenu', 'dépense']:
            raise ValueError("Le type doit être 'revenu' ou 'dépense'")
        
        if not self.description or not self.description.strip():
            raise ValueError("La description ne peut pas être vide")
    
    def to_dict(self):
        """Convertit la transaction en dictionnaire"""
        return {
            'id': self.id,
            'amount': self.amount,
            'description': self.description,
            'type': self.type,
            'category_id': self.category_id,
            'date': self.date.isoformat() if isinstance(self.date, date) else self.date
        }