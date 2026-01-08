#!/usr/bin/env python3
"""
Script pour vérifier la qualité du code (tests, couverture, linting, formatage)
"""

import subprocess
import sys

def run_command(name, command, fail_on_error=True):
    """Exécute une commande et affiche le résultat"""
    print(f"\n{'='*60}")
    print(f"🔍 {name}")
    print(f"{'='*60}\n")
    
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    
    if result.returncode != 0:
        print(f"❌ Échec: {name}")
        print(result.stderr)
        if fail_on_error:
            return False
    else:
        print(f"✅ Succès: {name}")
    
    return True

def quality_check():
    """Effectue tous les contrôles qualité"""
    
    print("🚀 Vérification de la qualité du code MyBudget")
    print("="*60)
    
    checks = []
    
    # 1. Tests unitaires
    checks.append(run_command(
        "Tests unitaires",
        "pytest tests/unit/ -v",
        fail_on_error=True
    ))
    
    # 2. Tests d'intégration
    checks.append(run_command(
        "Tests d'intégration",
        "pytest tests/integration/ -v",
        fail_on_error=True
    ))
    
    # 3. Tests BDD
    checks.append(run_command(
        "Tests BDD",
        "pytest tests/features/ -v",
        fail_on_error=True
    ))
    
    # 4. Couverture de code
    checks.append(run_command(
        "Couverture de code (≥80%)",
        "pytest --cov=src --cov-report=term-missing --cov-fail-under=80 -q",
        fail_on_error=True
    ))
    
    # 5. Flake8 (linting)
    checks.append(run_command(
        "Linting (Flake8)",
        "flake8 src/ --max-line-length=100 --exclude=__pycache__",
        fail_on_error=False  # Warning seulement
    ))
    
    # 6. Black (formatage)
    checks.append(run_command(
        "Formatage (Black)",
        "black src/ --check",
        fail_on_error=False  # Warning seulement
    ))
    
    # 7. MyPy (type checking)
    checks.append(run_command(
        "Type checking (MyPy)",
        "mypy src/ --ignore-missing-imports",
        fail_on_error=False  # Warning seulement
    ))
    
    # Résumé
    print(f"\n{'='*60}")
    print("📊 RÉSUMÉ")
    print(f"{'='*60}\n")
    
    passed = sum(checks)
    total = len(checks)
    
    print(f"Vérifications passées: {passed}/{total}")
    
    if all(checks[:4]):  # Les 4 premiers sont critiques
        print("\n✅ Tous les tests critiques passent !")
        print("   - Tests unitaires: ✅")
        print("   - Tests d'intégration: ✅")
        print("   - Tests BDD: ✅")
        print("   - Couverture ≥ 80%: ✅")
        
        if all(checks[4:]):
            print("\n🌟 Qualité de code excellente !")
            print("   - Linting: ✅")
            print("   - Formatage: ✅")
            print("   - Type checking: ✅")
        else:
            print("\n⚠️  Quelques avertissements sur la qualité du code")
            if not checks[4]:
                print("   - Linting: ⚠️  (voir détails ci-dessus)")
            if not checks[5]:
                print("   - Formatage: ⚠️  (exécutez: black src/)")
            if not checks[6]:
                print("   - Type checking: ⚠️  (voir détails ci-dessus)")
        
        return 0
    else:
        print("\n❌ Certains tests critiques ont échoué")
        if not checks[0]:
            print("   - Tests unitaires: ❌")
        if not checks[1]:
            print("   - Tests d'intégration: ❌")
        if not checks[2]:
            print("   - Tests BDD: ❌")
        if not checks[3]:
            print("   - Couverture: ❌")
        
        print("\n💡 Corrigez les erreurs et relancez le script")
        return 1

if __name__ == "__main__":
    sys.exit(quality_check())
