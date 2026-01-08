# tests/features/export.feature

Feature: Export des données
  En tant qu'utilisateur
  Je souhaite exporter mes transactions en CSV ou JSON
  Afin de les analyser avec d'autres outils

  Scenario: Export de toutes les transactions en CSV
    Given j'ai 5 transactions dans ma base de données
    When j'exporte toutes les transactions en CSV vers "export.csv"
    Then le fichier "export.csv" contient 5 lignes de données
    And le fichier CSV contient les colonnes: id, date, amount, description, type, category_id

  Scenario: Export filtré par catégorie en JSON
    Given j'ai des transactions dans 3 catégories différentes
    When j'exporte les transactions de la catégorie "alimentation" en JSON
    Then le fichier JSON contient uniquement les transactions de cette catégorie
    And le JSON contient le nombre total de transactions exportées

  Scenario: Export d'un résumé de budget
    Given un budget de 500 € pour "loisirs" en janvier 2026
    And des dépenses de 350 € en "loisirs" en janvier
    When j'exporte le résumé du budget en JSON
    Then le fichier contient le statut du budget
    And le fichier contient la liste des transactions de la période
