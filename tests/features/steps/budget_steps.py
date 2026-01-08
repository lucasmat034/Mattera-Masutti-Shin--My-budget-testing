# tests/features/steps/budget_steps.py

import pytest
from datetime import date
from pytest_bdd import scenarios, given, when, then, parsers
from src.models.transaction import Transaction
from src.models.budget import Budget

# Charger les scénarios
scenarios('../budget_alert.feature')

# Contexte partagé pour chaque scénario
@pytest.fixture
def context():
    return {
        'category_id': None,
        'budget_amount': 0,
        'period_start': None,
        'period_end': None,
        'initial_spending': 0,
        'new_transaction_amount': 0,
        'status': None,
        'alert_shown': False
    }


# ===== GIVEN steps =====

@given(parsers.re(r'un budget de (?P<amount>\d+(?:[.,]\d+)?) ?€? pour la catégorie "(?P<category>.+)" du (?P<start>\d{4}-\d{2}-\d{2}) au (?P<end>\d{4}-\d{2}-\d{2})'))
def set_budget(context, db_manager, budget_service, amount, category, start, end):
    """Définit un budget pour une catégorie"""
    # Récupérer l'ID de la catégorie
    categories = db_manager.execute_query(
        "SELECT id FROM categories WHERE name = ?", 
        (category,)
    )
    context['category_id'] = categories[0]['id']
    context['budget_amount'] = float(amount.replace(',', '.'))
    context['period_start'] = date.fromisoformat(start)
    context['period_end'] = date.fromisoformat(end)
    
    # Créer le budget
    b = Budget(
        category_id=context['category_id'],
        amount=context['budget_amount'],
        period_start=context['period_start'],
        period_end=context['period_end']
    )
    budget_service.create_budget(b)


@given(parsers.re(r'des dépenses existantes de (?P<amount>\d+(?:[.,]\d+)?) ?€? en "(?P<category>.+)"'))
def add_existing_spending(context, transaction_service, amount, category):
    """Ajoute des dépenses existantes"""
    # Ajouter une transaction pour simuler les dépenses existantes
    t = Transaction(
        amount=float(amount.replace(',', '.')),
        description="Dépenses existantes",
        type="dépense",
        category_id=context['category_id'],
        date=context['period_start']
    )
    transaction_service.add_transaction(t)
    context['initial_spending'] = float(amount.replace(',', '.'))


# ===== WHEN steps =====

@when(parsers.re(r"j'ajoute une nouvelle dépense de (?P<amount>\d+(?:[.,]\d+)?) ?€? en \"(?P<category>.+)\""))
def add_new_transaction(context, transaction_service, budget_service, amount, category):
    """Ajoute une nouvelle transaction"""
    amount = float(amount.replace(',', '.'))
    context['new_transaction_amount'] = amount
    # Ajouter la transaction
    t = Transaction(
        amount=amount,
        description="Nouvelle dépense",
        type="dépense",
        category_id=context['category_id'],
        date=context['period_start']
    )
    transaction_service.add_transaction(t)
    # Récupérer le statut du budget
    context['status'] = budget_service.get_budget_status(
        context['category_id'],
        context['period_start'],
        context['period_end']
    )
    # Simuler l'alerte
    if context['status']['is_exceeded']:
        context['alert_shown'] = True
    elif context['status']['percentage'] >= 80:
        context['alert_shown'] = True


# ===== THEN steps =====

@then(parsers.re(r'le total des dépenses est de (?P<expected>\d+(?:[.,]\d+)?) ?€?'))
def check_total_spending(context, expected):
    """Vérifie le total des dépenses"""
    expected = float(expected.replace(',', '.'))
    assert context['status']['spent'] == expected, \
        f"Total attendu: {expected}, obtenu: {context['status']['spent']}"


@then(parsers.re(r'le budget est dépassé de (?P<amount>\d+(?:[.,]\d+)?) ?€?'))
def check_budget_exceeded(context, amount):
    """Vérifie que le budget est dépassé du montant spécifié"""
    amount = float(amount.replace(',', '.'))
    assert context['status']['is_exceeded'], "Le budget devrait être dépassé"
    assert abs(context['status']['remaining']) == amount, \
        f"Dépassement attendu: {amount}, obtenu: {abs(context['status']['remaining'])}"


@then(parsers.re(r"l'alerte indique un dépassement de (?P<percentage>\d+(?:[.,]\d+)?)%"))
def check_alert_percentage(context, percentage):
    """Vérifie le pourcentage de dépassement"""
    percentage = float(percentage.replace(',', '.'))
    assert abs(context['status']['percentage'] - percentage) < 0.1, \
        f"Pourcentage attendu: {percentage}, obtenu: {context['status']['percentage']}"


@then(parsers.re(r'un avertissement de proximité est affiché \((?P<percentage>\d+(?:[.,]\d+)?)%\)'))
def check_warning_displayed(context, percentage):
    """Vérifie qu'un avertissement de proximité est affiché"""
    percentage = float(percentage.replace(',', '.'))
    assert context['status']['percentage'] >= 80, \
        "Un avertissement devrait être affiché (>= 80%)"
    assert context['alert_shown'], "Un avertissement devrait être affiché"


@then('une alerte est affichée à l\'utilisateur')
def check_alert_displayed(context):
    """Vérifie qu'une alerte est affichée"""
    assert context['alert_shown'], "Une alerte devrait être affichée"


@then('le budget n\'est pas dépassé')
def check_budget_not_exceeded(context):
    """Vérifie que le budget n'est pas dépassé"""
    assert not context['status']['is_exceeded'], "Le budget ne devrait pas être dépassé"


@then(parsers.parse('un avertissement de proximité est affiché ({percentage}%)'))
def check_warning_displayed(context, percentage):
    """Vérifie qu'un avertissement de proximité est affiché"""
    assert context['status']['percentage'] >= 80, \
        "Un avertissement devrait être affiché (>= 80%)"
    assert context['alert_shown'], "Un avertissement devrait être affiché"


@then('aucune alerte n\'est affichée')
def check_no_alert(context):
    """Vérifie qu'aucune alerte n'est affichée"""
    assert context['status']['percentage'] < 80, \
        "Le pourcentage est trop élevé, une alerte devrait être affichée"
    assert not context['alert_shown'], "Aucune alerte ne devrait être affichée"