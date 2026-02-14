# tests/features/reset.feature

Feature: Reinitialisation des donnees
  En tant qu'utilisateur
  Je souhaite reinitialiser les donnees (transactions et budgets)
  Afin de repartir de zero tout en conservant les categories

  Scenario: Reinitialiser apres avoir saisi des donnees
    Given des transactions existent
    And un budget existe
    When je reinitialise les donnees
    Then aucune transaction n'existe
    And aucun budget n'existe
    And les categories par defaut existent
