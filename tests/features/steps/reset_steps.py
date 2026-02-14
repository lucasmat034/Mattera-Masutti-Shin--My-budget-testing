# tests/features/steps/reset_steps.py

from pytest_bdd import scenarios, given, when, then

# Charger les scenarios
scenarios('../reset.feature')


@given('des transactions existent')
def existing_transactions(db_manager):
    db_manager.execute_update(
        "INSERT INTO transactions (amount, description, type, category_id, date) VALUES (?, ?, ?, ?, ?)",
        (10.0, "Test", "dépense", 1, "2026-01-10")
    )


@given('un budget existe')
def existing_budget(db_manager):
    db_manager.execute_update(
        "INSERT INTO budgets (category_id, amount, period_start, period_end) VALUES (?, ?, ?, ?)",
        (1, 100.0, "2026-01-01", "2026-01-31")
    )


@when('je reinitialise les donnees')
def reset_data(db_manager):
    db_manager.reset_data()


@then('aucune transaction n\'existe')
def no_transactions(db_manager):
    assert len(db_manager.execute_query("SELECT * FROM transactions")) == 0


@then('aucun budget n\'existe')
def no_budgets(db_manager):
    assert len(db_manager.execute_query("SELECT * FROM budgets")) == 0


@then('les categories par defaut existent')
def categories_exist(db_manager):
    assert len(db_manager.execute_query("SELECT * FROM categories")) == 6
