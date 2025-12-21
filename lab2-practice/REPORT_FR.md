# ESIEE Paris — Data Engineering I — Assignment 2
## Pipeline ETL & Entrepôt de Données en Schéma en Étoile

**Auteurs :** DIALLO Samba, DIOP Mouhamed  
**Date :** 30 octobre 2025  
**Année Académique :** 2025-2026  
**Programme :** Data & Applications - Engineering (FD)  
**Cours :** Data Engineering I

---

## Résumé Exécutif

Cette assignment a impliqué la construction d'un pipeline ETL (Extract, Transform, Load) complet pour transformer des données de vente opérationnelles depuis PostgreSQL vers un entrepôt de données en schéma en étoile optimisé pour les requêtes analytiques. Le projet a traité avec succès **42,4 millions d'événements**, **3 millions d'utilisateurs** et **166K produits** en utilisant Apache Spark.

**Réalisation Clé :** Réduction de l'empreinte de stockage de **4,2 GB (CSV)** à **0,4 GB (Parquet)** — une **compression de 90%** tout en maintenant l'intégrité complète des données.

---

## Objectifs

1. Extraire 7 tables de la base de données opérationnelle PostgreSQL
2. Construire 6 tables de dimensions (user, age, brand, category, product, date)
3. Créer une table de faits avec 42,4M d'événements
4. Implémenter des contrôles de qualité des données
5. Exporter vers plusieurs formats (CSV, Parquet)
6. Optimiser pour les requêtes analytiques

---

## Données d'Entrée

### Données Source
- **Base de Données :** PostgreSQL 17 (port 5432)
- **Hôte :** 127.0.0.1
- **Nom de la base :** esiee_full
- **Schéma :** retail
- **Utilisateur :** esiee_reader (lecture seule)

### Chemins d'Entrée
```
BASE_DIR = "/home/sable/de1-work/assignment2"

CSVs Sources :
├── user.csv           (3,022,290 lignes)
├── session.csv        (6,884,356 lignes)
├── product.csv        (166,794 lignes)
├── product_name.csv   (83 lignes)
├── events.csv         (42,418,541 lignes)
├── category.csv       (13 lignes)
└── brand.csv          (3,444 lignes)
```

### Chemins de Sortie
```
OUTPUT_BASE = "/home/sable/de1-work/assignment2/outputs/assignment2"

Sorties :
├── fact_events.csv/          (CSV non compressé)
├── fact_events.csv.snappy/   (CSV compressé)
└── fact_events.parquet/      (Parquet en colonnes)
```

---

## Architecture & Conception

### Conception du Schéma en Étoile

```
┌─────────────────────────────────────────────────┐
│              TABLE DE FAITS                      │
│              fact_events                         │
│  (42,418,541 lignes)                            │
│                                                  │
│  • date_key       → dim_date                    │
│  • user_key       → dim_user                    │
│  • age_key        → dim_age                     │
│  • product_key    → dim_product                 │
│  • brand_key      → dim_brand                   │
│  • category_key   → dim_category                │
│  • session_id     (clé métier)                  │
│  • event_time     (horodatage)                  │
│  • event_type     (view/cart/purchase/remove)   │
│  • price          (double, nullable)            │
└─────────────────────────────────────────────────┘
              │
              ├──────┬──────┬──────┬──────┬──────┐
              │      │      │      │      │      │
              ▼      ▼      ▼      ▼      ▼      ▼
      ┌─────────┐ ┌─────┐ ┌────────┐ ┌──────┐ ┌────────┐ ┌──────┐
      │dim_user │ │ age │ │product │ │brand │ │category│ │ date │
      │3.02M    │ │ 10  │ │166.7K  │ │3.4K  │ │  13    │ │  32  │
      └─────────┘ └─────┘ └────────┘ └──────┘ └────────┘ └──────┘
```

---

## Détails d'Implémentation

### Étapes du Pipeline ETL

1. **Extract :** Charger 7 fichiers CSV depuis l'export PostgreSQL
2. **Transform :** 
   - Créer des clés de substitution pour les dimensions
   - Construire des dimensions à variation lente de type-2 (groupes d'âge)
   - Agréger les métriques d'événements
3. **Load :** Écrire le schéma en étoile au format Parquet

### Stack Technologique

- **Apache Spark 4.0.1** - Traitement distribué
- **Python 3.10.18** - Langage principal
- **PostgreSQL 17** - Base de données source
- **Parquet** - Format de stockage

---

## Résultats

### Efficacité de Stockage

| Format | Taille | Ratio de Compression |
|--------|--------|---------------------|
| CSV (non compressé) | 4.2 GB | 1.0x |
| CSV (Snappy) | 1.2 GB | 3.5x |
| Parquet | 0.4 GB | 10.5x |

### Qualité des Données

- **Complétude :** 100% des enregistrements sources traités
- **Exactitude :** Toutes les relations de clés étrangères validées
- **Cohérence :** Le schéma en étoile est conforme aux meilleures pratiques de modélisation dimensionnelle

---

## Livrables

1. `assignment2_esiee.ipynb` - Notebook complet avec code exécuté
2. `REPORT.md` - Ce rapport
3. `assignment2_genai.md` - Documentation d'utilisation de l'IA
4. Fichiers de sortie :
   - `fact_events.csv/`
   - `fact_events.csv.snappy/`
   - `fact_events.parquet/`
   - Tables de dimensions (6 fichiers)

---

## Utilisation de l'IA Générative

Pour les détails sur l'utilisation de l'IA générative dans cette assignment, voir `assignment2_genai.md`.

**Résumé :** Nous avons utilisé **Claude Sonnet 4.5** (via GitHub Copilot) pour le débogage, l'optimisation de code et l'assistance à la documentation.

---

## Conclusion

L'assignment a démontré avec succès la capacité à :
- Concevoir et implémenter un entrepôt de données en schéma en étoile
- Traiter des jeux de données à grande échelle (42M+ lignes) avec Apache Spark
- Optimiser le stockage avec des formats en colonnes (Parquet)
- Appliquer les meilleures pratiques de data engineering

**Auteurs :** DIALLO Samba, DIOP Mouhamed  
**Date de Soumission :** 30 octobre 2025
