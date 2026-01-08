"""Application Flask pour MyBudget."""
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date
from decimal import Decimal

from src.database.db_manager import DatabaseManager
from src.services.transaction_service import TransactionService
from src.services.budget_service import BudgetService
from src.services.statistics_service import StatisticsService
from src.services.export_service import ExportService
from src.models.transaction import Transaction
from src.models.budget import Budget

app = Flask(__name__)
app.secret_key = 'mybudget-secret-key-2026'

# Services
db_manager = DatabaseManager()
transaction_service = TransactionService(db_manager)
budget_service = BudgetService(db_manager, transaction_service)
stats_service = StatisticsService(db_manager, transaction_service)
export_service = ExportService(transaction_service, db_manager)


def get_categories():
    """Récupère la liste des catégories."""
    query = "SELECT id, name FROM categories ORDER BY name"
    results = db_manager.execute_query(query)
    return {row['name']: row['id'] for row in results}


def get_category_name(category_id):
    """Récupère le nom d'une catégorie par son ID."""
    query = "SELECT name FROM categories WHERE id = ?"
    results = db_manager.execute_query(query, (category_id,))
    return results[0]['name'] if results else "inconnu"


@app.route('/')
def index():
    """Page d'accueil - Tableau de bord."""
    # Calculer les totaux
    all_transactions = transaction_service.list_transactions()
    
    total_revenue = sum(t.amount for t in all_transactions if t.type == "revenu")
    total_expense = sum(t.amount for t in all_transactions if t.type == "dépense")
    balance = total_revenue - total_expense
    
    # Récupérer les budgets
    budgets = budget_service.list_budgets()
    categories_map = get_categories()
    categories_reverse = {v: k for k, v in categories_map.items()}
    
    budgets_data = []
    for budget in budgets:
        category_name = categories_reverse.get(budget.category_id, "inconnu")
        status = budget_service.get_budget_status(
            budget.category_id,
            budget.period_start,
            budget.period_end
        )
        
        if status:
            percentage = status['percentage']
            if percentage >= 100:
                status_class = "danger"
                status_text = "Dépassé"
            elif percentage >= 90:
                status_class = "warning"
                status_text = "Attention"
            else:
                status_class = "success"
                status_text = "OK"
            
            budgets_data.append({
                'category': category_name.capitalize(),
                'amount': budget.amount,
                'spent': status['spent'],
                'remaining': status['remaining'],
                'percentage': percentage,
                'status_class': status_class,
                'status_text': status_text
            })
    
    return render_template('dashboard.html',
                         total_revenue=total_revenue,
                         total_expense=total_expense,
                         balance=balance,
                         budgets=budgets_data)


@app.route('/transactions')
def transactions():
    """Page des transactions."""
    # Récupérer les catégories
    categories = get_categories()
    
    # Filtres
    category_filter = request.args.get('category', 'all')
    type_filter = request.args.get('type', 'all')
    
    # Récupérer les transactions
    all_transactions = transaction_service.list_transactions()
    
    # Appliquer les filtres
    filtered_transactions = []
    for t in all_transactions:
        if category_filter != 'all':
            if t.category_id != categories.get(category_filter):
                continue
        
        if type_filter != 'all':
            if t.type != type_filter:
                continue
        
        filtered_transactions.append({
            'id': t.id,
            'date': t.date,
            'type': t.type,
            'category': get_category_name(t.category_id),
            'description': t.description,
            'amount': t.amount
        })
    
    # Trier par date décroissante
    filtered_transactions.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('transactions.html',
                         transactions=filtered_transactions,
                         categories=sorted(categories.keys()),
                         category_filter=category_filter,
                         type_filter=type_filter)


@app.route('/transactions/add', methods=['POST'])
def add_transaction():
    """Ajoute une nouvelle transaction."""
    try:
        amount = float(request.form['amount'])
        description = request.form['description'].strip()
        transaction_type = request.form['type']
        category_name = request.form['category']
        transaction_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        
        categories = get_categories()
        category_id = categories.get(category_name)
        
        if not category_id:
            flash('Catégorie invalide', 'error')
            return redirect(url_for('transactions'))
        
        transaction = Transaction(
            amount=amount,
            description=description,
            type=transaction_type,
            category_id=category_id,
            date=transaction_date
        )
        
        transaction_service.add_transaction(transaction)
        flash('Transaction ajoutée avec succès!', 'success')
        
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
    
    return redirect(url_for('transactions'))


@app.route('/transactions/delete/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    """Supprime une transaction."""
    try:
        transaction_service.delete_transaction(transaction_id)
        flash('Transaction supprimée avec succès!', 'success')
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
    
    return redirect(url_for('transactions'))


@app.route('/budgets')
def budgets():
    """Page des budgets."""
    categories = get_categories()
    categories_reverse = {v: k for k, v in categories.items()}
    
    # Récupérer les budgets
    all_budgets = budget_service.list_budgets()
    
    budgets_data = []
    for budget in all_budgets:
        category_name = categories_reverse.get(budget.category_id, "inconnu")
        status = budget_service.get_budget_status(
            budget.category_id,
            budget.period_start,
            budget.period_end
        )
        
        if status:
            budgets_data.append({
                'id': budget.id,
                'category': category_name.capitalize(),
                'amount': budget.amount,
                'period_start': budget.period_start,
                'period_end': budget.period_end,
                'spent': status['spent'],
                'remaining': status['remaining'],
                'percentage': status['percentage']
            })
    
    return render_template('budgets.html',
                         budgets=budgets_data,
                         categories=sorted(categories.keys()))


@app.route('/budgets/add', methods=['POST'])
def add_budget():
    """Crée un nouveau budget."""
    try:
        category_name = request.form['category']
        amount = float(request.form['amount'])
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        
        categories = get_categories()
        category_id = categories.get(category_name)
        
        if not category_id:
            flash('Catégorie invalide', 'error')
            return redirect(url_for('budgets'))
        
        budget = Budget(
            category_id=category_id,
            amount=amount,
            period_start=start_date,
            period_end=end_date
        )
        
        budget_service.create_budget(budget)
        flash('Budget créé avec succès!', 'success')
        
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')
    
    return redirect(url_for('budgets'))


@app.route('/statistics')
def statistics():
    """Page des statistiques."""
    year = request.args.get('year', date.today().year, type=int)
    month = request.args.get('month', date.today().month, type=int)
    
    try:
        # Résumé mensuel
        summary = stats_service.get_monthly_summary(year, month)
        
        # Moyenne quotidienne
        avg_daily = stats_service.get_average_daily_spending(year, month)
        
        # Prédiction
        prediction = stats_service.predict_end_of_month_spending(year, month)
        
        # Convertir by_category en liste pour le template
        categories_data = [
            {'name': cat.capitalize(), 'amount': float(amount)}
            for cat, amount in summary['by_category'].items()
        ]
        
        return render_template('statistics.html',
                             year=year,
                             month=month,
                             summary=summary,
                             categories_data=categories_data,
                             avg_daily=avg_daily,
                             prediction=prediction)
    
    except Exception as e:
        flash(f'Erreur lors du calcul des statistiques: {str(e)}', 'error')
        return render_template('statistics.html',
                             year=year,
                             month=month,
                             summary=None,
                             categories_data=[],
                             avg_daily=0,
                             prediction=0)


@app.route('/export/csv')
def export_csv():
    """Exporte les transactions en CSV."""
    try:
        filename = f"transactions_{date.today().isoformat()}.csv"
        export_service.export_transactions_to_csv(filename)
        flash(f'Transactions exportées vers {filename}', 'success')
    except Exception as e:
        flash(f'Erreur lors de l\'export: {str(e)}', 'error')
    
    return redirect(url_for('transactions'))


@app.route('/export/json')
def export_json():
    """Exporte les transactions en JSON."""
    try:
        filename = f"transactions_{date.today().isoformat()}.json"
        export_service.export_transactions_to_json(filename)
        flash(f'Transactions exportées vers {filename}', 'success')
    except Exception as e:
        flash(f'Erreur lors de l\'export: {str(e)}', 'error')
    
    return redirect(url_for('transactions'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
