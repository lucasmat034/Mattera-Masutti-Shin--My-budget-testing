#!/usr/bin/env python3
"""
Script pour vérifier la couverture de tests du projet
"""

import subprocess
import sys
import os

def check_coverage():
    """Vérifie la couverture de code et affiche un rapport"""
    
    print("🧪 Vérification de la couverture de tests...\n")
    
    # Exécuter pytest avec couverture
    result = subprocess.run(
        [
            "pytest",
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html",
            "--cov-fail-under=80",
            "-v"
        ],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    
    if result.returncode != 0:
        print("\n❌ Échec: La couverture est inférieure à 80% ou des tests ont échoué\n")
        print(result.stderr)
        
        # Afficher où se trouve le rapport HTML
        html_report = os.path.join(os.getcwd(), "htmlcov", "index.html")
        if os.path.exists(html_report):
            print(f"📊 Rapport détaillé disponible: {html_report}")
        
        sys.exit(1)
    else:
        print("\n✅ Succès: Couverture ≥ 80% et tous les tests passent !\n")
        
        # Afficher où se trouve le rapport HTML
        html_report = os.path.join(os.getcwd(), "htmlcov", "index.html")
        if os.path.exists(html_report):
            print(f"📊 Rapport détaillé disponible: {html_report}")
        
        print("\n💡 Pour ouvrir le rapport HTML:")
        print(f"   open {html_report}  # macOS")
        print(f"   xdg-open {html_report}  # Linux")
        print(f"   start {html_report}  # Windows")
        
        sys.exit(0)

if __name__ == "__main__":
    check_coverage()
