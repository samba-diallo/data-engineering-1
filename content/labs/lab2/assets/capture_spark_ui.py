#!/usr/bin/env python3
"""
Script pour capturer automatiquement des screenshots du Spark UI
Nécessite: selenium et un webdriver (Chrome/Firefox)
"""

import os
import time
from datetime import datetime
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
<<<<<<< HEAD
=======
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
>>>>>>> 07bd02a (lab2: Finalisation des livrables Lab 2 - Notebook nettoyé, métriques collectées, outputs et preuves complètes)
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium n'est pas installé")
    print("   Installez-le avec: pip install selenium")


class SparkUIScreenshot:
    """Capture automatique de screenshots du Spark UI"""
    
    def __init__(self, spark_ui_url="http://localhost:4040", output_dir="proof"):
        self.spark_ui_url = spark_ui_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.driver = None
    
    def setup_driver(self, headless=True):
        """Configure le webdriver Chrome"""
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium n'est pas disponible")
            return False
        
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✅ WebDriver Chrome initialisé")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation du WebDriver: {e}")
            print("   Assurez-vous que ChromeDriver est installé")
            return False
    
    def capture_page(self, url, filename, wait_time=2):
        """Capture une page spécifique"""
        if not self.driver:
            print("❌ WebDriver non initialisé")
            return False
        
        try:
            print(f"📸 Capture de {url}...")
            self.driver.get(url)
            time.sleep(wait_time)  # Attendre le chargement
            
            screenshot_path = self.output_dir / f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(str(screenshot_path))
            print(f"   ✅ Sauvegardé: {screenshot_path}")
            return True
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            return False
    
    def capture_all_pages(self):
        """Capture toutes les pages importantes du Spark UI"""
        pages = {
            'jobs': '/jobs/',
            'stages': '/stages/',
            'storage': '/storage/',
            'environment': '/environment/',
            'executors': '/executors/',
            'sql': '/SQL/'
        }
        
        print("\n" + "="*80)
        print("📸 CAPTURE DES PAGES SPARK UI")
        print("="*80 + "\n")
        
        for name, path in pages.items():
            url = f"{self.spark_ui_url}{path}"
            self.capture_page(url, f"spark_ui_{name}")
            time.sleep(1)  # Petite pause entre les captures
        
        print(f"\n✅ Captures sauvegardées dans: {self.output_dir}/")
    
    def capture_specific_job(self, job_id):
        """Capture la page d'un job spécifique"""
        url = f"{self.spark_ui_url}/jobs/job/?id={job_id}"
        return self.capture_page(url, f"spark_ui_job_{job_id}")
    
    def capture_specific_stage(self, stage_id):
        """Capture la page d'un stage spécifique"""
        url = f"{self.spark_ui_url}/stages/stage/?id={stage_id}&attempt=0"
        return self.capture_page(url, f"spark_ui_stage_{stage_id}")
    
    def close(self):
        """Ferme le webdriver"""
        if self.driver:
            self.driver.quit()
            print("✅ WebDriver fermé")


def capture_manual_instructions():
    """Affiche les instructions pour captures manuelles"""
    print("\n" + "="*80)
    print("📸 INSTRUCTIONS POUR CAPTURES MANUELLES")
    print("="*80)
    print("""
Si Selenium n'est pas disponible, capturez manuellement les pages suivantes:

1. Jobs Overview (http://localhost:4040/jobs/)
   - Vue d'ensemble de tous les jobs
   - Durée d'exécution de chaque job
   
2. Stages Overview (http://localhost:4040/stages/)
   - Liste de tous les stages
   - Métriques de shuffle
   
3. SQL Queries (http://localhost:4040/SQL/)
   - Plans d'exécution des requêtes
   - Vérifier les broadcast joins
   
4. Storage (http://localhost:4040/storage/)
   - Données mises en cache
   
5. Pour chaque job/stage important:
   - Cliquez sur le lien du job/stage
   - Capturez le DAG de visualisation
   - Capturez les métriques détaillées

Sauvegardez les captures dans: proof/screenshots/
Nommez les fichiers: spark_ui_[page]_[description].png
    """)
    print("="*80 + "\n")


def main():
    """Fonction principale"""
    print("="*80)
    print("🚀 SPARK UI SCREENSHOT TOOL - Lab 2")
    print("="*80 + "\n")
    
    if not SELENIUM_AVAILABLE:
        print("⚠️  Selenium n'est pas installé")
        print("   Pour l'installation automatique:")
        print("   pip install selenium")
        print("   Et téléchargez ChromeDriver: https://chromedriver.chromium.org/\n")
        capture_manual_instructions()
        return
    
    # Créer le dossier de screenshots
    screenshots_dir = Path("proof/screenshots")
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialiser le capteur
    capturer = SparkUIScreenshot(output_dir=screenshots_dir)
    
    if not capturer.setup_driver(headless=True):
        capture_manual_instructions()
        return
    
    try:
        # Capturer toutes les pages
        capturer.capture_all_pages()
        
        print("\n💡 Conseils:")
        print("   - Vérifiez les captures dans proof/screenshots/")
        print("   - Capturez des jobs/stages spécifiques si nécessaire")
        print("   - Ajoutez des annotations sur les captures importantes")
        
    finally:
        capturer.close()
    
    print("\n✅ Capture terminée!")


if __name__ == "__main__":
    main()
