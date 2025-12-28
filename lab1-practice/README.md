# Lab 1 : Analyse de Fréquence de Mots avec Apache Spark

**Auteurs :** DIALLO Samba, DIOP Mouhamed  
**Cours :** Data Engineering 1 - ESIEE 2025-2026  
**Date :** Octobre 2025

## Objectif

Implémenter une analyse de fréquence de mots sur des descriptions de produits en utilisant **Apache Spark**, avec deux approches :
- API **RDD** (Resilient Distributed Dataset)
- API **DataFrame** (SQL)

## Structure du Projet

```
lab1-practice/
├── DE1_Lab1_Notebook_EN.ipynb      # Notebook principal avec toutes les implémentations
├── assignment1_esiee.ipynb         # Notebook de travail
├── data/
│   ├── lab1_dataset_a.csv          # Dataset A (descriptions de produits)
│   ├── lab1_dataset_b.csv          # Dataset B (descriptions de produits)
│   └── lab1_metrics_log.csv        # Métriques de performance
├── outputs/
│   ├── top10_words.csv             # Top 10 mots (avec stopwords)
│   ├── top10_noStopWords.csv       # Top 10 mots (sans stopwords)
│   ├── top10_rdd.csv               # Résultats approche RDD
│   └── top10_df.csv                # Résultats approche DataFrame
├── README.md                        # Ce fichier
├── AI_USAGE.md                      # Documentation de l'utilisation de l'IA
└── RDD_vs_DataFrame_NOTE.md         # Notes de comparaison RDD vs DataFrame
```

## Étapes Réalisées

1. **Chargement des données** : Lecture des fichiers CSV contenant les descriptions de produits
2. **Nettoyage du texte** : Conversion en minuscules, suppression des caractères non-alphabétiques
3. **Tokenisation** : Découpage du texte en mots individuels
4. **Comptage de fréquences** : Calcul du nombre d'occurrences de chaque mot
5. **Filtrage des stopwords** : Suppression des mots communs ("le", "de", "pour", etc.)
6. **Export des résultats** : Sauvegarde des 10 mots les plus fréquents en CSV

## Approches Comparées

### Approche RDD
- Manipulations de bas niveau avec `map()`, `flatMap()`, `reduceByKey()`
- Contrôle total sur les transformations
- Adapté pour des traitements complexes et personnalisés

### Approche DataFrame
- API de haut niveau avec fonctions SQL (`lower()`, `regexp_replace()`, `explode()`)
- Optimisations automatiques du moteur Catalyst
- Meilleure performance pour les opérations structurées

## Comment Exécuter

```bash
# Activer l'environnement conda
conda activate de1-env

# Lancer Jupyter Notebook
jupyter notebook

# Ouvrir DE1_Lab1_Notebook_EN.ipynb et exécuter toutes les cellules
```

## Technologies Utilisées

- **Python** 3.10
- **Apache Spark** 4.0.1
- **PySpark** 4.0.1
- **Jupyter Notebook**
- **OpenJDK** 11

## Résultats

Les résultats montrent que l'approche DataFrame est plus performante et plus lisible que l'approche RDD pour ce type d'analyse structurée. Les fichiers de sortie contiennent les 10 mots les plus fréquents, avec et sans stopwords.

## Livrables

- Notebook Jupyter exécuté avec les résultats
- Fichiers CSV des top 10 mots
- Métriques de performance (temps d'exécution)
- Documentation de l'utilisation de l'IA (voir `AI_USAGE.md`)
