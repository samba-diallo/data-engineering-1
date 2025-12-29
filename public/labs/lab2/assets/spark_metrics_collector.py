#!/usr/bin/env python3
"""
Script de collecte automatique des métriques Spark UI
Auteurs: DIALLO Samba, DIOP Mouhamed
Cours: Data Engineering 1 - CEU
"""

import requests
import json
import csv
import time
from datetime import datetime
from pathlib import Path
import pandas as pd

class SparkMetricsCollector:
    """Collecteur de métriques depuis Spark UI via API REST"""
    
    def __init__(self, spark_ui_url="http://localhost:4040", app_id=None):
        """
        Args:
            spark_ui_url: URL du Spark UI (défaut: http://localhost:4040)
            app_id: ID de l'application Spark (auto-détecté si None)
        """
        self.spark_ui_url = spark_ui_url.rstrip('/')
        self.app_id = app_id
        self.metrics_file = Path("data/lab2_metrics_log.csv")
        
    def check_spark_ui_available(self):
        """Vérifie si Spark UI est accessible"""
        try:
            response = requests.get(f"{self.spark_ui_url}/api/v1/applications", timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def get_application_id(self):
        """Récupère l'ID de l'application Spark en cours"""
        try:
            response = requests.get(f"{self.spark_ui_url}/api/v1/applications")
            apps = response.json()
            if apps:
                # Prendre la première application (la plus récente)
                self.app_id = apps[0]['id']
                return self.app_id
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération de l'app ID: {e}")
            return None
    
    def get_job_metrics(self, job_id):
        """Récupère les métriques d'un job spécifique"""
        try:
            url = f"{self.spark_ui_url}/api/v1/applications/{self.app_id}/jobs/{job_id}"
            response = requests.get(url)
            return response.json()
        except Exception as e:
            print(f"Erreur lors de la récupération des métriques du job {job_id}: {e}")
            return None
    
    def get_stage_metrics(self, stage_id):
        """Récupère les métriques d'un stage spécifique"""
        try:
            url = f"{self.spark_ui_url}/api/v1/applications/{self.app_id}/stages/{stage_id}"
            response = requests.get(url)
            stages = response.json()
            if stages:
                return stages[0]  # Prendre la première tentative
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération des métriques du stage {stage_id}: {e}")
            return None
    
    def get_all_jobs(self):
        """Récupère tous les jobs de l'application"""
        try:
            url = f"{self.spark_ui_url}/api/v1/applications/{self.app_id}/jobs"
            response = requests.get(url)
            return response.json()
        except Exception as e:
            print(f"Erreur lors de la récupération de tous les jobs: {e}")
            return []
    
    def get_all_stages(self):
        """Récupère tous les stages de l'application"""
        try:
            url = f"{self.spark_ui_url}/api/v1/applications/{self.app_id}/stages"
            response = requests.get(url)
            return response.json()
        except Exception as e:
            print(f"Erreur lors de la récupération de tous les stages: {e}")
            return []
    
    def extract_metrics_from_stage(self, stage):
        """Extrait les métriques importantes d'un stage"""
        if not stage:
            return {}
        
        metrics = {
            'stage_id': stage.get('stageId', ''),
            'stage_name': stage.get('name', ''),
            'num_tasks': stage.get('numTasks', 0),
            'input_bytes': stage.get('inputBytes', 0),
            'input_records': stage.get('inputRecords', 0),
            'output_bytes': stage.get('outputBytes', 0),
            'output_records': stage.get('outputRecords', 0),
            'shuffle_read_bytes': stage.get('shuffleReadBytes', 0),
            'shuffle_read_records': stage.get('shuffleReadRecords', 0),
            'shuffle_write_bytes': stage.get('shuffleWriteBytes', 0),
            'shuffle_write_records': stage.get('shuffleWriteRecords', 0),
            'duration': stage.get('executorRunTime', 0),
            'status': stage.get('status', '')
        }
        return metrics
    
    def collect_current_metrics(self, run_id, task_name, note=""):
        """Collecte les métriques de la session Spark actuelle"""
        if not self.check_spark_ui_available():
            print(f"⚠️  Spark UI non accessible à {self.spark_ui_url}")
            print("   Assurez-vous que Spark est en cours d'exécution")
            return None
        
        if not self.app_id:
            self.get_application_id()
        
        if not self.app_id:
            print("❌ Impossible de récupérer l'ID de l'application")
            return None
        
        print(f"✅ Application Spark détectée: {self.app_id}")
        
        # Récupérer tous les stages
        stages = self.get_all_stages()
        
        if not stages:
            print("⚠️  Aucun stage trouvé")
            return None
        
        # Calculer les métriques agrégées
        total_input_bytes = 0
        total_shuffle_read = 0
        total_shuffle_write = 0
        files_read = 0
        
        for stage in stages:
            if stage.get('status') == 'COMPLETE':
                total_input_bytes += stage.get('inputBytes', 0)
                total_shuffle_read += stage.get('shuffleReadBytes', 0)
                total_shuffle_write += stage.get('shuffleWriteBytes', 0)
                files_read += stage.get('numTasks', 0)
        
        metrics_row = {
            'run_id': run_id,
            'task': task_name,
            'note': note,
            'files_read': files_read,
            'input_size_bytes': total_input_bytes,
            'shuffle_read_bytes': total_shuffle_read,
            'shuffle_write_bytes': total_shuffle_write,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"\n📊 Métriques collectées pour {task_name}:")
        print(f"   - Fichiers lus: {files_read}")
        print(f"   - Taille input: {total_input_bytes:,} bytes ({total_input_bytes/1024/1024:.2f} MB)")
        print(f"   - Shuffle read: {total_shuffle_read:,} bytes ({total_shuffle_read/1024/1024:.2f} MB)")
        print(f"   - Shuffle write: {total_shuffle_write:,} bytes ({total_shuffle_write/1024/1024:.2f} MB)")
        
        return metrics_row
    
    def save_metrics(self, metrics_row):
        """Sauvegarde les métriques dans le CSV"""
        # Créer le fichier s'il n'existe pas
        if not self.metrics_file.exists():
            self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.metrics_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=metrics_row.keys())
                writer.writeheader()
        
        # Ajouter la ligne
        with open(self.metrics_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=metrics_row.keys())
            writer.writerow(metrics_row)
        
        print(f"✅ Métriques sauvegardées dans {self.metrics_file}")
    
    def display_metrics_summary(self):
        """Affiche un résumé des métriques collectées"""
        if not self.metrics_file.exists():
            print("❌ Aucune métrique trouvée")
            return
        
        df = pd.read_csv(self.metrics_file)
        print("\n" + "="*80)
        print("📈 RÉSUMÉ DES MÉTRIQUES COLLECTÉES")
        print("="*80)
        print(df.to_string(index=False))
        print("="*80 + "\n")
    
    def get_spark_ui_urls(self):
        """Retourne les URLs importantes du Spark UI pour les captures"""
        if not self.app_id:
            self.get_application_id()
        
        urls = {
            'jobs': f"{self.spark_ui_url}/jobs/",
            'stages': f"{self.spark_ui_url}/stages/",
            'storage': f"{self.spark_ui_url}/storage/",
            'environment': f"{self.spark_ui_url}/environment/",
            'executors': f"{self.spark_ui_url}/executors/",
            'sql': f"{self.spark_ui_url}/SQL/"
        }
        
        print("\n🔗 URLs Spark UI pour captures d'écran:")
        for name, url in urls.items():
            print(f"   {name.capitalize()}: {url}")
        
        return urls


def main():
    """Fonction principale - Exemple d'utilisation"""
    print("="*80)
    print("🚀 SPARK METRICS COLLECTOR - Lab 2")
    print("="*80 + "\n")
    
    # Initialiser le collecteur
    collector = SparkMetricsCollector()
    
    # Vérifier la disponibilité
    if not collector.check_spark_ui_available():
        print("❌ Spark UI n'est pas accessible")
        print("   Veuillez démarrer votre notebook Spark d'abord")
        print(f"   Vérifiez que Spark UI est accessible à: {collector.spark_ui_url}")
        return
    
    print("✅ Spark UI est accessible\n")
    
    # Afficher les URLs pour captures
    collector.get_spark_ui_urls()
    
    print("\n" + "="*80)
    print("💡 INSTRUCTIONS D'UTILISATION")
    print("="*80)
    print("""
1. Dans votre notebook Spark, importez ce module:
   
   from spark_metrics_collector import SparkMetricsCollector
   collector = SparkMetricsCollector()

2. Avant chaque tâche importante, collectez les métriques:
   
   # Exemple: après l'ingestion des données
   metrics = collector.collect_current_metrics(
       run_id='r1',
       task_name='ingest_plan',
       note='Ingestion des données sources'
   )
   collector.save_metrics(metrics)

3. Tâches à tracker pour le Lab 2:
   - ingest_plan : Ingestion initiale
   - fact_join : Création de fact_sales
   - dim_creation : Création des dimensions
   - broadcast_test : Test avec broadcast
   
4. Pour afficher le résumé:
   
   collector.display_metrics_summary()

5. Ouvrez les URLs Spark UI affichées ci-dessus dans votre navigateur
   et prenez des captures d'écran pour le dossier proof/
    """)
    
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
