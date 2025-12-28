#!/usr/bin/env python3
"""
Script de lancement complet pour Lab 2
Exécute le notebook et collecte automatiquement les métriques
"""

import subprocess
import sys
from pathlib import Path

def check_dependencies():
    """Vérifie les dépendances nécessaires"""
    print("🔍 Vérification des dépendances...\n")
    
    dependencies = {
        'pyspark': 'Apache Spark',
        'pandas': 'Pandas',
        'requests': 'Requests',
    }
    
    missing = []
    for package, name in dependencies.items():
        try:
            __import__(package)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name} (manquant)")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Packages manquants: {', '.join(missing)}")
        print(f"   Installez-les avec: pip install {' '.join(missing)}")
        return False
    
    print("\n✅ Toutes les dépendances sont installées\n")
    return True

def setup_environment():
    """Configure l'environnement"""
    print("🔧 Configuration de l'environnement...\n")
    
    # Créer les dossiers nécessaires
    folders = [
        'data',
        'outputs/lab2',
        'proof',
        'proof/screenshots'
    ]
    
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {folder}/")
    
    print()

def run_jupyter_notebook():
    """Lance Jupyter Notebook"""
    print("="*80)
    print("🚀 LANCEMENT DU NOTEBOOK LAB 2")
    print("="*80)
    print("""
INSTRUCTIONS:

1. Le notebook va s'ouvrir dans votre navigateur
2. Exécutez les cellules une par une
3. Après chaque tâche importante, exécutez cette cellule:

   from spark_metrics_collector import SparkMetricsCollector
   collector = SparkMetricsCollector()
   
   metrics = collector.collect_current_metrics(
       run_id='r1',
       task_name='nom_de_la_tache',
       note='Description de la tâche'
   )
   collector.save_metrics(metrics)

4. Tâches à tracker:
   - ingest_plan : Après l'ingestion initiale
   - dim_creation : Après création des dimensions
   - fact_join : Après création de fact_sales
   - broadcast_test : Après tests broadcast

5. Pour les captures Spark UI:
   - Ouvrez http://localhost:4040 dans votre navigateur
   - Naviguez vers Jobs, Stages, SQL
   - Prenez des screenshots et sauvez dans proof/screenshots/

Appuyez sur Entrée pour continuer...
    """)
    input()
    
    # Lancer Jupyter
    notebook_path = "DE1_Lab2_Notebook_EN.ipynb"
    if Path(notebook_path).exists():
        print(f"\n📓 Lancement de {notebook_path}...\n")
        subprocess.run(['jupyter', 'notebook', notebook_path])
    else:
        print(f"❌ Notebook non trouvé: {notebook_path}")
        print("   Notebooks disponibles:")
        for nb in Path('.').glob('*.ipynb'):
            print(f"   - {nb}")

def display_post_execution_summary():
    """Affiche le résumé après exécution"""
    print("\n" + "="*80)
    print("📊 VÉRIFICATION DES LIVRABLES")
    print("="*80 + "\n")
    
    # Vérifier les outputs
    print("1. Résultats Parquet:")
    outputs_path = Path("outputs/lab2")
    if outputs_path.exists():
        for item in outputs_path.iterdir():
            if item.is_dir():
                count = len(list(item.rglob("*.parquet")))
                print(f"   ✅ {item.name}/ ({count} fichiers)")
    else:
        print("   ❌ Dossier outputs/lab2/ non trouvé")
    
    # Vérifier proof
    print("\n2. Dossier de preuve:")
    proof_items = {
        'proof/plan_ingest.txt': 'Plan d\'ingestion',
        'proof/plan_fact_join.txt': 'Plan de jointure fact',
        'proof/screenshots/': 'Captures d\'écran'
    }
    
    for path, desc in proof_items.items():
        if Path(path).exists():
            print(f"   ✅ {desc}")
        else:
            print(f"   ❌ {desc} (manquant)")
    
    # Vérifier métriques
    print("\n3. Métriques:")
    metrics_file = Path("data/lab2_metrics_log.csv")
    if metrics_file.exists():
        import pandas as pd
        df = pd.read_csv(metrics_file)
        filled_rows = df[df['input_size_bytes'].notna()].shape[0]
        total_rows = df.shape[0]
        print(f"   ✅ lab2_metrics_log.csv ({filled_rows}/{total_rows} lignes remplies)")
        
        if filled_rows < total_rows:
            print(f"   ⚠️  {total_rows - filled_rows} tâches sans métriques")
    else:
        print("   ❌ lab2_metrics_log.csv non trouvé")
    
    print("\n" + "="*80)
    print("💡 PROCHAINES ÉTAPES")
    print("="*80)
    print("""
1. Vérifiez que toutes les métriques sont collectées
2. Ajoutez les captures d'écran manquantes dans proof/screenshots/
3. Rédigez la note de conception (DESIGN_NOTES.md)
4. Vérifiez que le notebook est exécuté de bout en bout
5. Commitez et pushez sur GitHub
    """)
    print("="*80 + "\n")

def main():
    """Fonction principale"""
    print("="*80)
    print("🚀 LAB 2 - SETUP ET EXÉCUTION")
    print("="*80 + "\n")
    
    # Vérifier les dépendances
    if not check_dependencies():
        sys.exit(1)
    
    # Configuration
    setup_environment()
    
    # Menu
    print("Que voulez-vous faire?")
    print("1. Lancer le notebook et collecter les métriques")
    print("2. Capturer les screenshots Spark UI (automatique)")
    print("3. Afficher le résumé des livrables")
    print("4. Tout (recommandé)")
    print()
    
    choice = input("Votre choix (1-4): ").strip()
    
    if choice == '1':
        run_jupyter_notebook()
    elif choice == '2':
        print("\n📸 Lancement de la capture automatique...")
        subprocess.run([sys.executable, 'capture_spark_ui.py'])
    elif choice == '3':
        display_post_execution_summary()
    elif choice == '4':
        run_jupyter_notebook()
        print("\n" + "="*80)
        print("Voulez-vous capturer les screenshots Spark UI? (o/n): ", end='')
        if input().lower() == 'o':
            subprocess.run([sys.executable, 'capture_spark_ui.py'])
        display_post_execution_summary()
    else:
        print("❌ Choix invalide")
    
    print("\n✅ Terminé!")

if __name__ == "__main__":
    main()
