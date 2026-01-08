# tests/features/modification.feature

Feature: Modification et suppression de transactions
  En tant qu'utilisateur
  Je souhaite pouvoir modifier ou supprimer mes transactions
  Afin de corriger des erreurs de saisie

  Scenario: Modification du montant d'une transaction
    Given une transaction de 100 € pour "Courses" en alimentation
    When je modifie le montant à 150 €
    Then la transaction affiche un montant de 150 €
    And le total des dépenses est mis à jour

  Scenario: Suppression d'une transaction
    Given une transaction de 50 € pour "Restaurant"
    And le total des dépenses en alimentation est de 250 €
    When je supprime cette transaction
    Then la transaction n'existe plus
    And le total des dépenses en alimentation est de 200 €

  Scenario: Modification de la catégorie d'une transaction
    Given une transaction de 30 € classée en "loisirs"
    When je change la catégorie vers "alimentation"
    Then la transaction est dans la catégorie "alimentation"
    And le total de "loisirs" a diminué de 30 €
    And le total de "alimentation" a augmenté de 30 €
