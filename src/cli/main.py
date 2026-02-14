# src/cli/main.py

import click
from datetime import datetime, date
from tabulate import tabulate
from src.database.db_manager import DatabaseManager
from src.services.transaction_service import TransactionService
from src.services.budget_service import BudgetService
from src.services.export_service import ExportService
from src.models.transaction import Transaction
from src.models.budget import Budget

# Initialisation globale
db = DatabaseManager()
transaction_service = TransactionService(db)
budget_service = BudgetService(db, transaction_service)
export_service = ExportService(db, transaction_service)

@click.group()
def cli():
    """MyBudget - Gestionnaire de budget personnel"""
    pass

# ========== COMMANDES TRANSACTIONS ==========

@cli.command()
@click.argument('amount', type=float)
@click.argument('description')
@click.argument('category')
@click.argument('date_str', required=False)
@click.option('--type', '-t', default='dépense', type=click.Choice(['dépense', 'revenu']))
def add(amount, description, category, date_str, type):
    """Ajoute une transaction
    
    Exemple: mybudget add 25.50 "Courses Leclerc" alimentation 2026-01-06
    """
    try:
        # Récupérer l'ID de la catégorie
        categories = db.execute_query("SELECT id, name FROM categories WHERE name = ?", (category,))
        if not categories:
            click.echo(f"❌ Catégorie '{category}' inconnue")
            click.echo("Catégories disponibles: alimentation, logement, loisirs, transports, santé, autres")
            return
        
        category_id = categories[0]['id']
        
        # Parser la date
        if date_str:
            trans_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            trans_date = date.today()
        
        # Créer et enregistrer la transaction
        transaction = Transaction(
            amount=amount,
            description=description,
            type=type,
            category_id=category_id,
            date=trans_date
        )
        
        trans_id = transaction_service.add_transaction(transaction)
        click.echo(f"✅ Transaction ajoutée (ID: {trans_id})")
        
        # Vérifier si cela dépasse un budget
        check_budget_alert(category_id, trans_date)
        
    except ValueError as e:
        click.echo(f"❌ Erreur: {e}")
    except Exception as e:
        click.echo(f"❌ Erreur inattendue: {e}")


@cli.command()
@click.option('--category', '-c', help='Filtrer par catégorie')
@click.option('--start', '-s', help='Date de début (YYYY-MM-DD)')
@click.option('--end', '-e', help='Date de fin (YYYY-MM-DD)')
@click.option('--type', '-t', type=click.Choice(['dépense', 'revenu']), help='Type de transaction')
def list(category, start, end, type):
    """Liste les transactions avec filtres optionnels
    
    Exemple: mybudget list --category alimentation --start 2026-01-01
    """
    try:
        # Convertir la catégorie en ID si fournie
        category_id = None
        if category:
            categories = db.execute_query("SELECT id FROM categories WHERE name = ?", (category,))
            if categories:
                category_id = categories[0]['id']
        
        # Parser les dates
        start_date = datetime.strptime(start, '%Y-%m-%d').date() if start else None
        end_date = datetime.strptime(end, '%Y-%m-%d').date() if end else None
        
        # Récupérer les transactions
        transactions = transaction_service.list_transactions(
            category_id=category_id,
            start_date=start_date,
            end_date=end_date,
            transaction_type=type
        )
        
        if not transactions:
            click.echo("Aucune transaction trouvée.")
            return
        
        # Récupérer les noms de catégories
        cat_map = {
            row['id']: row['name'] 
            for row in db.execute_query("SELECT id, name FROM categories")
        }
        
        # Formater les données pour le tableau
        table_data = [
            [
                t.id,
                t.date,
                t.type,
                cat_map.get(t.category_id, 'N/A'),
                t.description,
                f"{t.amount:.2f} €"
            ]
            for t in transactions
        ]
        
        headers = ['ID', 'Date', 'Type', 'Catégorie', 'Description', 'Montant']
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        click.echo(f"\nTotal: {len(transactions)} transaction(s)")
        
    except Exception as e:
        click.echo(f"❌ Erreur: {e}")


# ========== COMMANDES BUDGETS ==========

@cli.command()
@click.argument('category')
@click.argument('amount', type=float)
@click.argument('start_date')
@click.argument('end_date')
def budget(category, amount, start_date, end_date):
    """Crée un budget pour une catégorie
    
    Exemple: mybudget budget alimentation 300 2026-01-01 2026-01-31
    """
    try:
        # Récupérer l'ID de la catégorie
        categories = db.execute_query("SELECT id FROM categories WHERE name = ?", (category,))
        if not categories:
            click.echo(f"❌ Catégorie '{category}' inconnue")
            return
        
        category_id = categories[0]['id']
        
        # Parser les dates
        period_start = datetime.strptime(start_date, '%Y-%m-%d').date()
        period_end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Créer le budget
        b = Budget(
            category_id=category_id,
            amount=amount,
            period_start=period_start,
            period_end=period_end
        )
        
        budget_id = budget_service.create_budget(b)
        click.echo(f"✅ Budget créé (ID: {budget_id})")
        click.echo(f"   {category}: {amount} € du {start_date} au {end_date}")
        
    except ValueError as e:
        click.echo(f"❌ Erreur: {e}")
    except Exception as e:
        click.echo(f"❌ Erreur: {e}")


@cli.command()
@click.argument('category')
@click.argument('start_date')
@click.argument('end_date')
def status(category, start_date, end_date):
    """Affiche le statut d'un budget
    
    Exemple: mybudget status alimentation 2026-01-01 2026-01-31
    """
    try:
        # Récupérer l'ID de la catégorie
        categories = db.execute_query("SELECT id FROM categories WHERE name = ?", (category,))
        if not categories:
            click.echo(f"❌ Catégorie '{category}' inconnue")
            return
        
        category_id = categories[0]['id']
        
        # Parser les dates
        period_start = datetime.strptime(start_date, '%Y-%m-%d').date()
        period_end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Récupérer le statut
        status = budget_service.get_budget_status(category_id, period_start, period_end)
        
        if not status:
            click.echo(f"❌ Aucun budget trouvé pour {category} sur cette période")
            return
        
        # Affichage
        click.echo(f"\n📊 Budget {category} ({start_date} → {end_date})")
        click.echo(f"   Budget fixé  : {status['budget_amount']:.2f} €")
        click.echo(f"   Dépensé      : {status['spent']:.2f} €")
        click.echo(f"   Restant      : {status['remaining']:.2f} €")
        click.echo(f"   Consommation : {status['percentage']}%")
        
        if status['is_exceeded']:
            click.echo(f"\n⚠️  ALERTE: Budget dépassé de {abs(status['remaining']):.2f} € !")
        elif status['percentage'] >= 80:
            click.echo(f"\n⚠️  Attention: Vous avez déjà consommé {status['percentage']}% de votre budget")
        
    except Exception as e:
        click.echo(f"❌ Erreur: {e}")


@cli.command()
@click.option('--format', 'format_', type=click.Choice(['csv', 'json']), required=True)
@click.option('--output', '-o', required=True, help='Chemin du fichier a creer')
@click.option('--category', '-c', help='Filtrer par categorie')
@click.option('--start', '-s', help='Date de debut (YYYY-MM-DD)')
@click.option('--end', '-e', help='Date de fin (YYYY-MM-DD)')
@click.option('--pretty/--compact', default=True, help='Format JSON lisible')
def export(format_, output, category, start, end, pretty):
    """Exporte les transactions en CSV ou JSON
    
    Exemple: mybudget export --format csv --output export.csv
    """
    try:
        category_id = None
        if category:
            categories = db.execute_query("SELECT id FROM categories WHERE name = ?", (category,))
            if not categories:
                click.echo(f"❌ Categorie '{category}' inconnue")
                return
            category_id = categories[0]['id']

        start_date = datetime.strptime(start, '%Y-%m-%d').date() if start else None
        end_date = datetime.strptime(end, '%Y-%m-%d').date() if end else None

        if format_ == 'csv':
            count = export_service.export_transactions_to_csv(
                output,
                category_id=category_id,
                start_date=start_date,
                end_date=end_date
            )
        else:
            count = export_service.export_transactions_to_json(
                output,
                category_id=category_id,
                start_date=start_date,
                end_date=end_date,
                pretty=pretty
            )

        click.echo(f"✅ Export termine: {count} transaction(s) -> {output}")
    except Exception as e:
        click.echo(f"❌ Erreur: {e}")


@cli.command(name='export-budget')
@click.argument('category')
@click.argument('start_date')
@click.argument('end_date')
@click.option('--output', '-o', required=True, help='Chemin du fichier JSON a creer')
def export_budget(category, start_date, end_date, output):
    """Exporte un resume de budget en JSON
    
    Exemple: mybudget export-budget alimentation 2026-01-01 2026-01-31 -o budget.json
    """
    try:
        categories = db.execute_query("SELECT id FROM categories WHERE name = ?", (category,))
        if not categories:
            click.echo(f"❌ Categorie '{category}' inconnue")
            return
        category_id = categories[0]['id']

        period_start = datetime.strptime(start_date, '%Y-%m-%d').date()
        period_end = datetime.strptime(end_date, '%Y-%m-%d').date()

        success = export_service.export_budget_summary_to_json(
            output,
            category_id=category_id,
            period_start=period_start,
            period_end=period_end
        )
        if not success:
            click.echo("❌ Aucun budget trouve pour cette periode")
            return

        click.echo(f"✅ Export termine -> {output}")
    except Exception as e:
        click.echo(f"❌ Erreur: {e}")


@cli.command()
@click.option('--yes', is_flag=True, help='Confirmer la reinitialisation sans prompt')
def reset(yes):
    """Reinitialise les transactions et budgets
    
    Exemple: mybudget reset --yes
    """
    try:
        if not yes:
            confirmed = click.confirm(
                "Reinitialiser toutes les transactions et budgets ?",
                default=False
            )
            if not confirmed:
                click.echo("Operation annulee.")
                return
        db.reset_data()
        click.echo("âœ… Donnees reinitialisees (transactions et budgets supprimes, categories conservees).")
    except Exception as e:
        click.echo(f"âŒ Erreur: {e}")


def check_budget_alert(category_id, trans_date):
    """Vérifie si une transaction dépasse un budget"""
    # Trouver les budgets actifs pour cette catégorie
    query = """
    SELECT * FROM budgets
    WHERE category_id = ?
    AND period_start <= ?
    AND period_end >= ?
    """
    budgets = db.execute_query(query, (category_id, trans_date, trans_date))
    
    for budget_data in budgets:
        status = budget_service.get_budget_status(
            category_id,
            datetime.strptime(budget_data['period_start'], '%Y-%m-%d').date(),
            datetime.strptime(budget_data['period_end'], '%Y-%m-%d').date()
        )
        
        if status and status['is_exceeded']:
            cat_name = db.execute_query(
                "SELECT name FROM categories WHERE id = ?", 
                (category_id,)
            )[0]['name']
            click.echo(f"\n⚠️  ALERTE: Budget {cat_name} dépassé de {abs(status['remaining']):.2f} € !")


if __name__ == '__main__':
    cli()
