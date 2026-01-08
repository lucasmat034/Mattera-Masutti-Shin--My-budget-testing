# src/services/export_service.py

import csv
import json
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional
from src.database.db_manager import DatabaseManager
from src.services.transaction_service import TransactionService

class ExportService:
    """Service pour exporter les données en CSV et JSON"""
    
    def __init__(self, db_manager: DatabaseManager, transaction_service: TransactionService):
        self.db = db_manager
        self.transaction_service = transaction_service
    
    def export_transactions_to_csv(
        self,
        filepath: str,
        category_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> int:
        """
        Exporte les transactions en CSV
        
        Args:
            filepath: Chemin du fichier CSV de sortie
            category_id: Filtrer par catégorie (optionnel)
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)
            
        Returns:
            Nombre de transactions exportées
        """
        # Récupérer les transactions
        transactions = self.transaction_service.list_transactions(
            category_id=category_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Créer le dossier parent si nécessaire
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Écrire le CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'date', 'amount', 'description', 'type', 'category_id']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for t in transactions:
                writer.writerow({
                    'id': t.id,
                    'date': t.date.isoformat(),
                    'amount': t.amount,
                    'description': t.description,
                    'type': t.type,
                    'category_id': t.category_id
                })
        
        return len(transactions)
    
    def export_transactions_to_json(
        self,
        filepath: str,
        category_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        pretty: bool = True
    ) -> int:
        """
        Exporte les transactions en JSON
        
        Args:
            filepath: Chemin du fichier JSON de sortie
            category_id: Filtrer par catégorie (optionnel)
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)
            pretty: Formater le JSON avec indentation
            
        Returns:
            Nombre de transactions exportées
        """
        # Récupérer les transactions
        transactions = self.transaction_service.list_transactions(
            category_id=category_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Convertir en dictionnaires
        data = {
            'export_date': datetime.now().isoformat(),
            'count': len(transactions),
            'transactions': [t.to_dict() for t in transactions]
        }
        
        # Créer le dossier parent si nécessaire
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Écrire le JSON
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            if pretty:
                json.dump(data, jsonfile, indent=2, ensure_ascii=False)
            else:
                json.dump(data, jsonfile, ensure_ascii=False)
        
        return len(transactions)
    
    def export_budget_summary_to_json(
        self,
        filepath: str,
        category_id: int,
        period_start: date,
        period_end: date
    ) -> bool:
        """
        Exporte un résumé de budget en JSON
        
        Args:
            filepath: Chemin du fichier JSON de sortie
            category_id: ID de la catégorie
            period_start: Date de début de période
            period_end: Date de fin de période
            
        Returns:
            True si l'export a réussi, False sinon
        """
        from src.services.budget_service import BudgetService
        budget_service = BudgetService(self.db, self.transaction_service)
        
        # Récupérer le statut du budget
        status = budget_service.get_budget_status(category_id, period_start, period_end)
        
        if not status:
            return False
        
        # Récupérer le nom de la catégorie
        category_data = self.db.execute_query(
            "SELECT name FROM categories WHERE id = ?",
            (category_id,)
        )
        category_name = category_data[0]['name'] if category_data else "Unknown"
        
        # Récupérer les transactions de la période
        transactions = self.transaction_service.list_transactions(
            category_id=category_id,
            start_date=period_start,
            end_date=period_end,
            transaction_type='dépense'
        )
        
        # Construire le résumé
        data = {
            'export_date': datetime.now().isoformat(),
            'category': category_name,
            'period': {
                'start': period_start.isoformat(),
                'end': period_end.isoformat()
            },
            'budget': status,
            'transactions': [t.to_dict() for t in transactions]
        }
        
        # Créer le dossier parent si nécessaire
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Écrire le JSON
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
        
        return True
