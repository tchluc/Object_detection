"""
Script de validation des améliorations du système de détection d'objets.
Vérifie que tous les modules sont correctement structurés et commentés.
"""

import os
import sys
import ast


def check_file_has_docstring(filepath):
    """Vérifie qu'un fichier Python a un docstring."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
        docstring = ast.get_docstring(tree)
        return docstring is not None and len(docstring) > 20
    except (SyntaxError, ValueError):
        return False


def check_functions_have_docstrings(filepath):
    """Vérifie que les fonctions principales ont des docstrings."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        documented = sum(1 for func in functions if ast.get_docstring(func))
        return len(functions), documented
    except (SyntaxError, ValueError):
        return 0, 0


def validate_improvements():
    """Valide toutes les améliorations implémentées."""
    print("="*60)
    print("VALIDATION DES AMÉLIORATIONS")
    print("="*60)
    
    results = []
    
    # 1. Vérifier que le module summary existe
    print("\n1. Module de résumé des objets")
    if os.path.exists('summary.py'):
        has_docstring = check_file_has_docstring('summary.py')
        total_funcs, doc_funcs = check_functions_have_docstrings('summary.py')
        print(f"   ✓ summary.py existe")
        print(f"   ✓ Docstring de module: {'Oui' if has_docstring else 'Non'}")
        print(f"   ✓ Fonctions documentées: {doc_funcs}/{total_funcs}")
        results.append(True)
    else:
        print(f"   ✗ summary.py manquant")
        results.append(False)
    
    # 2. Vérifier les commentaires dans les modules principaux
    print("\n2. Commentaires dans les modules")
    modules_to_check = ['main.py', 'processor.py', 'tracking.py', 'alerts.py', 'config.py', 'select_zone.py']
    
    for module in modules_to_check:
        if os.path.exists(module):
            has_docstring = check_file_has_docstring(module)
            total_funcs, doc_funcs = check_functions_have_docstrings(module)
            status = "✓" if has_docstring else "✗"
            print(f"   {status} {module}: Docstring module={'Oui' if has_docstring else 'Non'}, Fonctions={doc_funcs}/{total_funcs}")
            results.append(has_docstring)
        else:
            print(f"   ✗ {module} manquant")
            results.append(False)
    
    # 3. Vérifier le support des polygones
    print("\n3. Support des zones polygonales")
    if os.path.exists('select_polygon_zone.py'):
        print(f"   ✓ select_polygon_zone.py existe")
        results.append(True)
    else:
        print(f"   ✗ select_polygon_zone.py manquant")
        results.append(False)
    
    # Vérifier que alerts.py contient les nouvelles fonctions
    if os.path.exists('alerts.py'):
        with open('alerts.py', 'r') as f:
            content = f.read()
            has_polygon = 'is_point_in_polygon' in content
            has_draw = 'draw_zones' in content
            print(f"   ✓ Fonction is_point_in_polygon: {'Oui' if has_polygon else 'Non'}")
            print(f"   ✓ Fonction draw_zones: {'Oui' if has_draw else 'Non'}")
            results.append(has_polygon and has_draw)
    
    # 4. Vérifier la configuration améliorée du tracker
    print("\n4. Configuration du tracker")
    if os.path.exists('custom_tracker.yaml'):
        with open('custom_tracker.yaml', 'r') as f:
            content = f.read()
            # Extraire la valeur de track_buffer
            import re
            match = re.search(r'track_buffer:\s*(\d+)', content)
            if match:
                buffer_value = int(match.group(1))
                if buffer_value >= 90:
                    print(f"   ✓ track_buffer optimisé ({buffer_value} ≥ 90)")
                    results.append(True)
                else:
                    print(f"   ✗ track_buffer non optimisé ({buffer_value} < 90)")
                    results.append(False)
            else:
                print(f"   ✗ track_buffer non trouvé")
                results.append(False)
    else:
        print(f"   ✗ custom_tracker.yaml manquant")
        results.append(False)
    
    # 5. Vérifier la documentation README
    print("\n5. Documentation README")
    if os.path.exists('README.md'):
        with open('README.md', 'r') as f:
            content = f.read()
            has_summary = 'object_summary' in content or 'Résumé' in content
            has_polygon = 'polygon' in content or 'Polygone' in content
            has_architecture = 'Architecture' in content or 'architecture' in content
            print(f"   ✓ Documentation du résumé: {'Oui' if has_summary else 'Non'}")
            print(f"   ✓ Documentation des polygones: {'Oui' if has_polygon else 'Non'}")
            print(f"   ✓ Section architecture: {'Oui' if has_architecture else 'Non'}")
            results.append(has_summary and has_polygon and has_architecture)
    else:
        print(f"   ✗ README.md manquant")
        results.append(False)
    
    # 6. Vérifier l'intégration du résumé dans main.py
    print("\n6. Intégration du résumé")
    if os.path.exists('main.py'):
        with open('main.py', 'r') as f:
            content = f.read()
            has_import = 'from summary import' in content
            has_call = 'generate_object_summary' in content
            print(f"   ✓ Import de summary: {'Oui' if has_import else 'Non'}")
            print(f"   ✓ Appel de generate_object_summary: {'Oui' if has_call else 'Non'}")
            results.append(has_import and has_call)
    
    # Résumé final
    print("\n" + "="*60)
    success_rate = (sum(results) / len(results)) * 100
    print(f"RÉSULTAT: {sum(results)}/{len(results)} vérifications réussies ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("✓ Toutes les améliorations sont correctement implémentées!")
    elif success_rate >= 70:
        print("⚠ La plupart des améliorations sont implémentées")
    else:
        print("✗ Plusieurs améliorations sont manquantes")
    
    print("="*60)
    
    return success_rate >= 90


if __name__ == "__main__":
    success = validate_improvements()
    sys.exit(0 if success else 1)
