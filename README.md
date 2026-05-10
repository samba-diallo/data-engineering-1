# Data Engineering 1 

Ce dépôt contient les travaux pratiques et le projet final du cours Data Engineering 1.

## Structure du dépôt

- **lab1-practice/** : Introduction à PySpark avec manipulation de DataFrames
- **lab2-practice/** : Data warehouse avec Star Schema et transformations
- **lab3-practice/** : Lakehouse architecture et optimisations
- **projet-final/** : Projet final - Pipeline de données complet

## Note sur les fichiers volumineux

**Fichiers non inclus sur GitHub** : Les fichiers Parquet générés dans `lab2-practice/retail_dw_20250826/` (~2,5 GB, 800+ fichiers) sont exclus du dépôt GitHub en raison de leur taille. Ces fichiers sont générés localement lors de l'exécution des notebooks PySpark et restent disponibles dans votre environnement local.

Pour régénérer ces fichiers localement, exécutez les notebooks dans le dossier `lab2-practice/`.

## Documentation GenAI

Chaque lab contient un fichier `assignmentX_genai.md` documentant l'utilisation des outils d'IA générative pour résoudre les exercices.
