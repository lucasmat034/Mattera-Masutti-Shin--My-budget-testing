# tests/features/budget_alert.feature

Feature: Alerte de dépassement de budget
  En tant qu'utilisateur
  Je souhaite être alerté quand une dépense fait dépasser mon budget
  Afin de mieux contrôler mes finances

  Scenario: Dépassement du budget alimentation
    Given un budget de 300 € pour la catégorie "alimentation" du 2026-01-01 au 2026-01-31
    And des dépenses existantes de 290 € en "alimentation"
    When j'ajoute une nouvelle dépense de 20 € en "alimentation"
    Then le total des dépenses est de 310 €
    And le budget est dépassé de 10 €
    And une alerte est affichée à l'utilisateur
    And l'alerte indique un dépassement de 103.3%

  Scenario: Budget proche de la limite (80%)
    Given un budget de 500 € pour la catégorie "loisirs" du 2026-01-01 au 2026-01-31
    And des dépenses existantes de 350 € en "loisirs"
    When j'ajoute une nouvelle dépense de 50 € en "loisirs"
    Then le total des dépenses est de 400 €
    And le budget n'est pas dépassé
    But un avertissement de proximité est affiché (80%)

  Scenario: Budget non dépassé avec marge confortable
    Given un budget de 1000 € pour la catégorie "logement" du 2026-01-01 au 2026-01-31
    And des dépenses existantes de 200 € en "logement"
    When j'ajoute une nouvelle dépense de 100 € en "logement"
    Then le total des dépenses est de 300 €
    And le budget n'est pas dépassé
    And aucune alerte n'est affichée