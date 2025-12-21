# Assignment 1 : Comptage de Mots avec Apache Spark

> **Cours :** Data Engineering 1  
> **Étudiant :** Samba Diallo (@samba-diallo)  
> **Date de soumission :** 22 octobre 2025  
> **Environnement :** Python 3.10, PySpark 4.0.1, Ubuntu Linux

---

## Table des Matières

- [Aperçu](#aperçu)
- [Structure du Projet](#structure-du-projet)
- [Configuration de l'Environnement](#configuration-de-lenvironnement)
- [Détails d'Implémentation](#détails-dimplémentation)
- [Résultats](#résultats)
- [Comment Exécuter](#comment-exécuter)
- [Technologies Utilisées](#technologies-utilisées)
- [Divulgation de l'Assistance IA](#divulgation-de-lassistance-ia)
- [Licence](#licence)

---

## Aperçu

Ce projet implémente une **analyse de fréquence des mots** sur des descriptions de produits en utilisant **Apache Spark**. L'assignment démontre la maîtrise des approches **basées sur RDD** et **basées sur DataFrame** pour le traitement distribué des données.

### Objectifs

1. Charger et traiter des données CSV contenant des descriptions de produits
2. Nettoyer et tokeniser les données textuelles (minuscules, suppression des caractères non-alphabétiques)
3. Compter les fréquences des mots en utilisant les APIs RDD et DataFrame
4. Supprimer les stopwords et ré-analyser les fréquences
5. Exporter les 10 mots les plus fréquents vers des fichiers CSV

---

## Structure du Projet

```
data-engineering-assignment1/
│
├── notebook.ipynb                  # Notebook Jupyter principal avec toutes les implémentations
├── a1-brand.csv                    # Jeu de données d'entrée (descriptions de produits)
├── top10_words.csv/                # Sortie : Top 10 mots (avec stopwords)
│   └── part-00000-*.csv
├── top10_noStopWords.csv/          # Sortie : Top 10 mots (sans stopwords)
│   └── part-00000-*.csv
├── submission_info.json            # Métadonnées d'environnement et d'exécution
├── README.md                       # Ce fichier
└── .gitignore                      # Règles Git ignore
```

---

## Configuration de l'Environnement

### Prérequis

- **Python :** 3.10+
- **Java :** OpenJDK 11 (requis pour Spark)
- **Apache Spark :** 4.0.1
- **Conda/Miniconda :** Pour la gestion de l'environnement

### Étapes d'Installation

```bash
# 1. Créer et activer l'environnement conda
conda create -n de1-env python=3.10 openjdk=11 -y
conda activate de1-env

# 2. Installer PySpark et les dépendances
conda install -c conda-forge pyspark
pip install jupyter pandas pytz

# 3. Définir les variables d'environnement
export JAVA_HOME=$CONDA_PREFIX
export SPARK_HOME=$CONDA_PREFIX/lib/python3.10/site-packages/pyspark

# 4. Vérifier l'installation
python -c "import pyspark; print(pyspark.__version__)"
java -version
```

### Informations Système

- **Système d'Exploitation :** Ubuntu Linux (ThinkPad X1 Yoga 3ème Gen)
- **Version Python :** 3.10.x
- **Version PySpark :** 4.0.1
- **Version Java :** OpenJDK 11
- **Fuseau Horaire :** UTC
- **Répertoire de Travail :** `~/Documents/data engineering1/`

---

## Détails d'Implémentation

### 1. Approche Basée sur RDD

```python
# Charger les données comme RDD
lines = sc.textFile("a1-brand.csv")

# Nettoyer et tokeniser
words = (
    lines
    .map(lambda s: re.sub('[^a-z]', ' ', s.lower()))
    .flatMap(lambda s: s.split())
    .filter(lambda w: len(w) >= 2)
)

# Compter les fréquences
word_counts = (
    words
    .map(lambda w: (w, 1))
    .reduceByKey(lambda a, b: a + b)
    .sortBy(lambda kv: (-kv[1], kv[0]))
)
```

### 2. Approche Basée sur DataFrame

```python
# Charger les données comme DataFrame
df = spark.read.option("header", "true").csv("a1-brand.csv")

# Nettoyer, tokeniser et compter
word_counts = (
    df
    .select("description")
    .withColumn("clean", lower(col("description")))
    .withColumn("clean", regexp_replace(col("clean"), "[^a-z]", " "))
    .withColumn("words", split(col("clean"), "\\s+"))
    .withColumn("word", explode(col("words")))
    .filter(length(col("word")) >= 2)
    .groupBy("word")
    .agg(count("*").alias("count"))
    .orderBy(col("count").desc(), col("word"))
)
```

### 3. Suppression des Stopwords

```python
from pyspark.ml.feature import StopWordsRemover

remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")
# Appliquer pour supprimer les mots communs comme "the", "in", "for", etc.
```

### Étapes Clés du Traitement

1. **Nettoyage du Texte :**
   - Conversion en minuscules
   - Remplacement des caractères non-alphabétiques par des espaces
   - Division sur les espaces blancs

2. **Tokenisation :**
   - Division du texte en mots individuels
   - Filtrage des tokens de longueur < 2

3. **Analyse de Fréquence :**
   - Comptage des occurrences de chaque mot
   - Tri par fréquence (décroissant) et alphabétiquement

4. **Filtrage des Stopwords :**
   - Suppression des mots anglais communs en utilisant le `StopWordsRemover` de Spark ML

---

## Résultats

### Top 10 Mots (Avec Stopwords)

Les mots les plus fréquents incluent les stopwords communs comme "the", "in", "for", etc.

### Top 10 Mots (Sans Stopwords)

Après suppression des stopwords, des mots de contenu plus significatifs émergent, fournissant de meilleures informations sur les descriptions de produits.

**Note :** Les résultats complets sont disponibles dans :
- `top10_words.csv/part-00000-*.csv`
- `top10_noStopWords.csv/part-00000-*.csv`

---

## Comment Exécuter

### Option 1 : Jupyter Notebook

```bash
# Naviguer vers le répertoire du projet
cd ~/Documents/data\ engineering1/

# Activer l'environnement
conda activate de1-env

# Lancer Jupyter
jupyter notebook

# Ouvrir notebook.ipynb et exécuter toutes les cellules
```

### Option 2 : VS Code avec Extension Jupyter

```bash
# Naviguer vers le répertoire du projet
cd ~/Documents/data\ engineering1/

# Ouvrir dans VS Code
code .

# Ouvrir notebook.ipynb
# Sélectionner le noyau : de1-env
# Exécuter toutes les cellules (Shift+Enter)
```

### Configuration Spark

```python
spark = (
    SparkSession.builder
    .appName("Assignment1")
    .master("local[*]")
    .config("spark.sql.shuffle.partitions", "10")  # Optimisé pour local
    .config("spark.driver.memory", "2g")
    .getOrCreate()
)
```

- **Interface Spark :** http://localhost:4040 (quand SparkSession est active)

---

## Technologies Utilisées

| Technologie | Version | But |
|-------------|---------|-----|
| **Python** | 3.10+ | Langage de programmation |
| **Apache Spark** | 4.0.1 | Traitement distribué des données |
| **PySpark** | 4.0.1 | API Python pour Spark |
| **Jupyter** | Dernière | Développement interactif |
| **Pandas** | Dernière | Visualisation des données |
| **OpenJDK** | 11 | Runtime Java pour Spark |
| **Conda** | Dernière | Gestion de l'environnement |

### Bibliothèques Clés

- `pyspark.sql` : API DataFrame
- `pyspark.rdd` : API RDD
- `pyspark.ml.feature.StopWordsRemover` : Suppression des stopwords
- `re` : Expressions régulières pour le nettoyage de texte

---

## Divulgation de l'Assistance IA

### Utilisation de l'Intelligence Artificielle

Ce projet a été réalisé **avec l'assistance d'outils IA** dans le cadre du processus d'apprentissage. Spécifiquement :

- **Outil IA Utilisé :** Anthropic Claude Sonnet 4.5 (via GitHub Copilot Chat)
- **Nature de l'Assistance :**
  - Débogage des problèmes de configuration PySpark (JAVA_HOME, SPARK_HOME)
  - Compréhension des différences entre les APIs RDD et DataFrame
  - Suggestions d'optimisation de code (éviter les UDFs, partitions de shuffle)
  - Documentation et structure du README
  - Meilleures pratiques pour l'optimisation des performances Spark

### Résultats d'Apprentissage

Bien que l'IA ait aidé au dépannage technique et aux explications :

1. **Implémentations principales** (comptage de mots RDD, transformations DataFrame) ont été écrites sur la base de la compréhension des concepts Spark
2. **Approche de résolution de problèmes** a été guidée par les explications de l'IA mais exécutée de manière indépendante
3. **Analyse et comparaisons** (RDD vs DataFrame) reflètent la compréhension personnelle acquise au cours du processus

### Déclaration de Transparence

Je crois en **l'utilisation transparente de l'IA comme outil d'apprentissage**. L'assistance IA a aidé à accélérer le débogage et à clarifier les concepts, de manière similaire à consulter la documentation, Stack Overflow, ou un assistant pédagogique. Le travail final représente ma compréhension et mon application des principes de Data Engineering avec Apache Spark.

---

## Considérations de Performance

### Optimisations Appliquées

1. **Fonctions Natives plutôt que UDFs :**
   - Utilisation de `pyspark.sql.functions` (lower, regexp_replace, split)
   - Évitement des UDFs Python pour de meilleures performances

2. **Réduction des Partitions de Shuffle :**
   - Définition de `spark.sql.shuffle.partitions = 10` pour l'exécution locale
   - La valeur par défaut (200) est excessive pour les exécutions sur machine unique

3. **Filtrage Efficace :**
   - Filtrage des valeurs nulles tôt dans le pipeline
   - Suppression des chaînes vides avant l'explosion des tableaux

4. **Sortie en Fichier Unique :**
   - Utilisation de `.coalesce(1)` pour l'export CSV
   - Évite les fichiers part multiples en sortie

---

## Comparaison : RDD vs DataFrame

### Les Résultats Sont-ils Identiques ?

**En pratique, les résultats peuvent différer** en raison de :

1. **Analyse CSV :**
   - **RDD :** Traite chaque ligne comme texte brut (inclut toutes les colonnes)
   - **DataFrame :** Analyse la structure CSV, extrait uniquement la colonne "description"

2. **Gestion de l'En-tête :**
   - **RDD :** Peut inclure la ligne d'en-tête dans le comptage de mots
   - **DataFrame :** Saute automatiquement l'en-tête avec `option("header", "true")`

3. **Logique de Traitement :**
   - Les deux appliquent les mêmes transformations (minuscules, regex, filtrage)
   - L'approche DataFrame est plus précise pour les données CSV structurées

**Conclusion :** DataFrame donne des résultats plus corrects pour analyser spécifiquement la colonne "description".

---

## Nettoyage

```python
# Arrêter SparkSession
spark.stop()

# Supprimer les fichiers temporaires (optionnel)
rm -rf spark-warehouse/ metastore_db/ derby.log
```

---

## Licence

Ce projet est soumis dans le cadre du cours **Data Engineering 1**.

**Intégrité Académique :** Ce travail représente ma propre compréhension et implémentation, réalisée avec l'assistance IA divulguée ci-dessus.

---

## Contact

**Étudiant :** Samba Diallo  
**GitHub :** [@samba-diallo](https://github.com/samba-diallo)  
**Date de Soumission :** 22 octobre 2025 (UTC)

---

## Remerciements

- **Instructeurs du Cours** pour avoir fourni l'assignment et le jeu de données
- **Anthropic Claude** pour l'assistance technique et les explications
- **Communauté Apache Spark** pour l'excellente documentation
- **Stack Overflow** pour les références de dépannage

---

**Si ce dépôt vous a aidé, pensez à lui donner une étoile !**
