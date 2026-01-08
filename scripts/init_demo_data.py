#!/usr/bin/env python3
"""
Script pour initialiser des données de démonstration dans MyBudget
"""

from datetime import date, timedelta
from src.database.db_manager import DatabaseManager
from src.services.transaction_service import TransactionService
from src.services.budget_service import BudgetService
from src.models.transaction import Transaction
from src.models.budget import Budget

def init_demo_data():
    """Initialise la base de données avec des données de démonstration"""
    
    print("🚀 Initialisation des données de démonstration...")
    
    # Initialiser les services
    db = DatabaseManager()
    transaction_service = TransactionService(db)
    budget_service = BudgetService(db, transaction_service)
    
    today = date.today()
    start_of_month = date(today.year, today.month, 1)
    if today.month == 12:
        end_of_month = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        end_of_month = date(today.year, today.month + 1, 1) - timedelta(days=1)
    
    print(f"\n📅 Période: {start_of_month} → {end_of_month}\n")
    
    # Créer des budgets
    print("💰 Création des budgets...")
    budgets = [
        Budget(1, 400, start_of_month, end_of_month),  # alimentation
        Budget(2, 800, start_of_month, end_of_month),  # logement
        Budget(3, 300, start_of_month, end_of_month),  # loisirs
        Budget(4, 150, start_of_month, end_of_month),  # transports
        Budget(5, 100, start_of_month, end_of_month),  # santé
    ]
    
    for budget in budgets:
        budget_id = budget_service.create_budget(budget)
        cat_name = db.execute_query("SELECT name FROM categories WHERE id = ?", (budget.category_id,))[0]['name']
        print(f"  ✅ Budget {cat_name}: {budget.amount} €")
    
    # Créer des transactions
    print("\n📝 Création des transactions...")
    
    transactions = [
        # Alimentation
        Transaction(65.50, "Courses Leclerc", "dépense", 1, start_of_month + timedelta(days=2)),
        Transaction(8.90, "Boulangerie", "dépense", 1, start_of_month + timedelta(days=3)),
        Transaction(45.20, "Marché", "dépense", 1, start_of_month + timedelta(days=5)),
        Transaction(78.30, "Supermarché", "dépense", 1, start_of_month + timedelta(days=8)),
        Transaction(12.50, "Restaurant rapide", "dépense", 1, start_of_month + timedelta(days=10)),
        Transaction(55.00, "Courses hebdo", "dépense", 1, start_of_month + timedelta(days=12)),
        
        # Logement
        Transaction(650.00, "Loyer", "dépense", 2, start_of_month + timedelta(days=1)),
        Transaction(45.00, "Électricité", "dépense", 2, start_of_month + timedelta(days=5)),
        Transaction(25.00, "Internet", "dépense", 2, start_of_month + timedelta(days=6)),
        
        # Loisirs
        Transaction(12.50, "Cinéma", "dépense", 3, start_of_month + timedelta(days=7)),
        Transaction(45.00, "Concert", "dépense", 3, start_of_month + timedelta(days=14)),
        Transaction(28.90, "Livres", "dépense", 3, start_of_month + timedelta(days=11)),
        Transaction(60.00, "Sortie restaurant", "dépense", 3, start_of_month + timedelta(days=15)),
        
        # Transports
        Transaction(75.00, "Abonnement transport", "dépense", 4, start_of_month + timedelta(days=1)),
        Transaction(45.00, "Essence", "dépense", 4, start_of_month + timedelta(days=9)),
        
        # Santé
        Transaction(25.00, "Pharmacie", "dépense", 5, start_of_month + timedelta(days=6)),
        Transaction(50.00, "Médecin", "dépense", 5, start_of_month + timedelta(days=13)),
        
        # Revenus
        Transaction(2500.00, "Salaire", "revenu", 6, start_of_month + timedelta(days=1)),
        Transaction(150.00, "Freelance", "revenu", 6, start_of_month + timedelta(days=10)),
    ]
    
    for t in transactions:
        t_id = transaction_service.add_transaction(t)
        symbol = "💰" if t.type == "revenu" else "💸"
        print(f"  {symbol} {t.description}: {t.amount} € ({t.date})")
    
    print(f"\n✅ {len(transactions)} transactions créées")
    
    # Afficher un résumé
    print("\n📊 Résumé des budgets:\n")
    
    categories = db.execute_query("SELECT * FROM categories WHERE id <= 5")
    
    for cat in categories:
        status = budget_service.get_budget_status(cat['id'], start_of_month, end_of_month)
        if status:
            emoji = "⚠️" if status['is_exceeded'] else "✅"
            print(f"{emoji} {cat['name'].capitalize()}")
            print(f"   Budget: {status['budget_amount']:.2f} €")
            print(f"   Dépensé: {status['spent']:.2f} € ({status['percentage']}%)")
            print(f"   Restant: {status['remaining']:.2f} €")
            print()
    
    # Calculer le total
    all_transactions = transaction_service.list_transactions(
        start_date=start_of_month,
        end_date=end_of_month
    )
    
    total_revenus = sum(t.amount for t in all_transactions if t.type == 'revenu')
    total_depenses = sum(t.amount for t in all_transactions if t.type == 'dépense')
    balance = total_revenus - total_depenses
    
    print("💵 BILAN GLOBAL")
    print(f"   Revenus: {total_revenus:.2f} €")
    print(f"   Dépenses: {total_depenses:.2f} €")
    print(f"   Balance: {balance:.2f} €")
    
    print("\n✨ Données de démonstration initialisées avec succès !")
    print(f"\n💡 Essayez: mybudget status alimentation {start_of_month} {end_of_month}")
    
    db.close()

if __name__ == "__main__":
    init_demo_data()
