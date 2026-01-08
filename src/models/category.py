# src/models/category.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class Category:
    """Modèle représentant une catégorie"""
    name: str
    id: Optional[int] = None
    
    def __post_init__(self):
        """Validation des données"""
        if not self.name or not self.name.strip():
            raise ValueError("Le nom de la catégorie ne peut pas être vide")
    
    def to_dict(self):
        """Convertit la catégorie en dictionnaire"""
        return {
            'id': self.id,
            'name': self.name
        }
