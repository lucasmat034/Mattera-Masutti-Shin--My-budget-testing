# src/models/budget.py

from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Budget:
    """Modèle représentant un budget pour une catégorie"""
    category_id: int
    amount: float
    period_start: date
    period_end: date
    id: Optional[int] = None
    
    def __post_init__(self):
        """Validation des données"""
        if self.amount <= 0:
            raise ValueError("Le montant du budget doit être positif")
        
        if self.period_start >= self.period_end:
            raise ValueError("La date de début doit être antérieure à la date de fin")
    
    def is_active_for_date(self, check_date: date) -> bool:
        """Vérifie si le budget est actif pour une date donnée"""
        return self.period_start <= check_date <= self.period_end
    
    def to_dict(self):
        """Convertit le budget en dictionnaire"""
        return {
            'id': self.id,
            'category_id': self.category_id,
            'amount': self.amount,
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat()
        }
