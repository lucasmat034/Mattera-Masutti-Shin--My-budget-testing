# src/database/db_manager.py

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Any

class DatabaseManager:
    """Gestionnaire de base de données SQLite pour MyBudget"""
    
    def __init__(self, db_path: str = "data/budget.db"):
        """
        Initialise la connexion à la base de données
        
        Args:
            db_path: Chemin vers le fichier de base de données
                    Utiliser ":memory:" pour une base en mémoire (tests)
        """
        self.db_path = db_path
        
        # Créer le dossier data s'il n'existe pas
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom
        self._create_tables()
    
    def _create_tables(self):
        """Crée les tables de la base de données si elles n'existent pas"""
        
        # Table des catégories
        self.connection.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        """)
        
        # Table des transactions
        self.connection.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            description TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('revenu', 'dépense')),
            category_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
        """)
        
        # Table des budgets
        self.connection.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            period_start TEXT NOT NULL,
            period_end TEXT NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
        """)
        
        # Initialiser les catégories par défaut
        self._init_default_categories()
        
        self.connection.commit()
    
    def _init_default_categories(self):
        """Initialise les catégories par défaut"""
        default_categories = [
            'alimentation',
            'logement',
            'loisirs',
            'transports',
            'santé',
            'autres'
        ]
        
        for category in default_categories:
            try:
                self.connection.execute(
                    "INSERT INTO categories (name) VALUES (?)",
                    (category,)
                )
            except sqlite3.IntegrityError:
                # La catégorie existe déjà
                pass
        
        self.connection.commit()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Exécute une requête SELECT et retourne les résultats
        
        Args:
            query: La requête SQL à exécuter
            params: Les paramètres de la requête
            
        Returns:
            Liste de dictionnaires contenant les résultats
        """
        cursor = self.connection.execute(query, params)
        rows = cursor.fetchall()
        
        # Convertir les Row en dictionnaires
        return [dict(row) for row in rows]
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Exécute une requête INSERT, UPDATE ou DELETE
        
        Args:
            query: La requête SQL à exécuter
            params: Les paramètres de la requête
            
        Returns:
            ID de la dernière ligne insérée (pour INSERT) ou nombre de lignes affectées
        """
        cursor = self.connection.execute(query, params)
        self.connection.commit()
        return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
    
    def close(self):
        """Ferme la connexion à la base de données"""
        if self.connection:
            self.connection.close()
    
    def __enter__(self):
        """Support pour le context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support pour le context manager"""
        self.close()
