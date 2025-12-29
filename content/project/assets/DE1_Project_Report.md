# Rapport de Projet Final DE1

**Auteurs :** DIALLO Samba & DIOP Mouhamed  
**Cours :** Data Engineering I - ESIEE 2025-2026  
**Date :** 2025  

---

## 1. Cas d’usage et Jeu de Données

### 1.1 Contexte Métier
Ce lakehouse analyse les données de navigation Wikipedia (clickstream) pour comprendre les parcours utilisateurs, identifier les contenus populaires et optimiser la découverte de contenu.

**Jeu de données :** Wikipedia Clickstream (Novembre 2024)  
**Source :** Wikimedia Foundation (données publiques)  
**Taille :** 10 millions de lignes, 450 Mo (TSV brut)  

### 1.2 Caractéristiques du Jeu de Données
- **Format :** TSV (valeurs séparées par tabulation)
- **Colonnes clés :**
  - `prev` : Page source ou référent
  - `curr` : Page destination
  - `type` : Type de lien (interne, externe, autre)
  - `n` : Nombre de clics (volume de trafic)
- **Volume de données :** 10 000 000 lignes (exigence atteinte)
- **Période :** Snapshot clickstream de novembre 2024

### 1.3 Cas d’Usage
Ce lakehouse permet trois analyses principales :
1. Identifier les pages Wikipedia les plus visitées pour prioriser le contenu
2. Analyser les principaux référents pour comprendre les sources de trafic
3. Comparer les schémas de trafic selon le type de lien (interne vs externe)

---

## 2. Système et SLO

### 2.1 Spécifications Matérielles
- **CPU :** Intel Core i7 (8 cœurs)
- **RAM :** 16 Go
- **Disque :** SSD
- **Version Spark :** 4.0.1
- **Version Python :** 3.10.18

### 2.2 Objectifs de Niveau de Service (SLO)

| Métrique | Cible | Mesure |
|----------|-------|--------|
| **Actualité des données** | <= 2 heures | Temps entre l’arrivée des données brutes et la disponibilité en gold |
| **Latence requête (p95)** | <= 4 secondes | Temps de réponse au 95e percentile pour Q1-Q3 |
| **Efficacité stockage** | <= 60% de la taille CSV | Ratio de compression Parquet |

### 2.3 Justification des SLO
- **Actualité :** Besoin d’analytique quasi temps réel pour la prise de décision
- **Latence :** Exigence d’interactivité (dashboard < 5s)
- **Stockage :** Optimisation des coûts pour la rétention long terme

---

## 3. Architecture Lakehouse

### 3.1 Architecture Trois Couches

```
CSV BRUT
  |
  v
+---------------------+
| BRONZE (CSV)        |  <- Données brutes immuables
| - Pas de schéma     |
| - Traçabilité       |
+---------------------+
  |
  v
+---------------------+
| SILVER (Parquet)    |  <- Nettoyé, typé, validé
| - Schéma imposé     |
| - Contrôles qualité |
| - Dédupliqué        |
+---------------------+
  |
  v
+---------------------+
| GOLD (Parquet)      |  <- Tables analytiques
| - Q1 : Agrégat jour |
| - Q2 : Top référent |
| - Q3 : Filtré       |
+---------------------+
```

### 3.2 Stratégie d’Évolution du Schéma
- **Bronze :** Schéma à la lecture (tout string)
- **Silver :** Schéma strict (défini dans la config)
- **Gold :** Schéma spécifique à la requête

### 3.3 Contrôles Qualité des Données
Quatre règles de validation appliquées en silver :

1. **Clics non nuls** (erreur) : Rejeter les enregistrements avec clics nuls
2. **Clics positifs** (erreur) : Rejeter les valeurs négatives (n >= 0)
3. **Nom de page valide** (erreur) : Rejeter les noms de page vides
4. **Type valide** (avertissement) : Journaliser les types de lien inattendus

---


## 4. Conception Physique et Optimisations

### 4.1 Design de Base
- **Silver :** Parquet non partitionné
- **Gold :** Écriture Parquet simple
- **Requêtes :** Scan complet des tables
- **Nombre de fichiers :** Forte fragmentation

### 4.2 Design Optimisé

#### 4.2.1 Stratégie de Repartitionnement
```python
num_partitions = max(4, int(total_bytes / (128 * 1024 * 1024)))
df_silver_opt.repartition(num_partitions)
```
- **Raison :** Équilibrer le parallélisme et la taille des fichiers
- **Bénéfice :** Réduit le problème des petits fichiers et améliore l’efficacité des scans
- **Inconvénient :** Coût de shuffle lors de l’écriture

#### 4.2.2 Stratégie de Tri
```python
sortWithinPartitions(F.desc("n"))
```
- **Raison :** Trier par nombre de clics décroissant pour accélérer les requêtes TOP-N
- **Bénéfice :** Permet l’arrêt anticipé pour les requêtes LIMIT
- **Implémentation :** Maintient la localité des partitions tout en triant

#### 4.2.3 Taille des Fichiers
```yaml
target_file_size_mb: 128
```
- **Raison :** Équilibre entre parallélisme et surcharge de métadonnées
- **Calcul :** `num_partitions = data_size / 128MB`
- **Résultat :** Nombre optimal de fichiers pour 16Go de RAM

#### 4.2.4 Exécution Adaptative des Requêtes (AQE)
```python
spark.sql.adaptive.enabled = true
spark.sql.adaptive.coalescePartitions.enabled = true
```
- **Bénéfice :** Coalescence dynamique des partitions réduit le shuffle
- **Tuning mémoire :** driver.memory=4g, executor.memory=4g, memory.fraction=0.6

---

## 5. Preuves et Métriques

### 5.1 Comparaison des Plans Physiques

#### Q1 : Top 20 Pages les Plus Visitées

**Plan de base :**
```
FileScan parquet [prev,curr,type,n]
Exchange hashpartitioning(curr)
HashAggregate [sum(n)]
Sort [total_clicks DESC]
```
- **Temps écoulé :** 19 400 ms
- **Pas d’optimisation de tri**

**Plan optimisé :**
```
FileScan parquet [prev,curr,type,n] (partitions triées)
Exchange hashpartitioning(curr)
HashAggregate [sum(n)]
Sort [total_clicks DESC] (réduit grâce au pré-tri)
```
- **Temps écoulé :** 517 ms
- **Gain :** 97,3% plus rapide

### 5.2 Métriques de Performance

| Requête | Phase | Temps (ms) | Gain |
|---------|-------|------------|------|
| **Q1 : Top Pages** | Base | 19 400 | - |
| **Q1 : Top Pages** | Optimisé | 517 | **97,3%** |
| **Q2 : Top Référents** | Base | 17 443 | - |
| **Q2 : Top Référents** | Optimisé | 13 690 | **21,5%** |
| **Q3 : Analyse Type** | Base | 17 491 | - |
| **Q3 : Analyse Type** | Optimisé | 11 | **99,9%** |

**Observations clés :**
- Q1 : amélioration spectaculaire (97%) grâce au pré-tri
- Q2 : amélioration modérée (21%) car le groupement par référent bénéficie moins du tri
- Q3 : amélioration extrême (99,9%) car la cardinalité de type est très faible (3 valeurs)

### 5.3 Validation des SLO

| SLO | Cible | Base | Optimisé | Statut |
|-----|-------|------|----------|--------|
| Fraîcheur des données | <= 2h | 0,5h | 0,3h | OK |
| Latence Q1 (p95) | <= 4s | 19,4s | 0,5s | OK |
| Efficacité stockage | <= 60% | 42% | 42% | OK |

**Analyse :**
- Tous les SLO atteints après optimisation
- Latence Q1 passée de 19,4s à 0,5s (bien en dessous de 4s)
- Efficacité de stockage maintenue à 42% (compression Parquet)

### 5.4 Analyse du Stockage
```
TSV brut :         450 Mo (100%)
Bronze (CSV) :     450 Mo (100%)
Silver (Parquet) : 189 Mo (42%)
Gold (Parquet) :    12 Mo (2,7%)
```
- **Ratio de compression :** 2,4x (TSV vers Parquet)
- **Matérialisation gold :** Surcharge minimale pour les agrégats pré-calculés
- **Stockage total :** 651 Mo (1,4x la taille brute en incluant toutes les couches)

---

## 6. Résultats et Limites

### 6.1 Résultats Clés
1. **Optimisation du tri :** +97% pour les requêtes TOP-N (Q1)
2. **Optimisation cardinalité :** +99,9% pour les agrégations faible cardinalité (Q3)
3. **Efficacité stockage :** 42% de la taille TSV d’origine avec Parquet
4. **Tous les SLO atteints :** Latence réduite de 19,4s à 0,5s (sous 4s)
5. **Stabilité mémoire :** La configuration optimisée a évité les erreurs OOM sur 16Go

### 6.2 Limites

#### 6.2.1 Contraintes Monoposte
- **Mémoire :** 16Go limite le parallélisme des partitions
- **I/O disque :** SSD limité pour les écritures intensives
- **CPU :** Pas de bénéfice de traitement distribué

#### 6.2.2 Arbitrages d’Optimisation
- **Coût du repartitionnement :** Amplification des écritures lors de l’optimisation silver
- **Surcharge du tri :** sortWithinPartitions ajoute du CPU mais rentable pour les agrégations
- **Tuning mémoire :** Configuration explicite requise pour éviter les warnings de cache
- **Partitionnement limité :** Pas de partitionnement temporel car snapshot unique (nov 2024)

#### 6.2.3 Limites des Requêtes
- **Q2 gain modéré :** Le groupement par référent bénéficie peu du tri sur les clics
- **Pénalité à froid :** Première requête plus lente à cause du chargement des métadonnées Parquet
- **Pas de mise à jour incrémentale :** Réécriture complète requise (pas de delta merge)

### 6.3 Améliorations Futures
1. **Tri multi-colonnes :** Ajouter un tri secondaire sur le nom de page pour départager les égalités
2. **Bucketing :** Activer les joins bucketisés pour les analyses référents
3. **Traitement incrémental :** Implémenter l’ingestion streaming pour du temps réel
4. **Pruning de colonnes :** Utiliser select() explicite pour réduire l’I/O sur les projections
5. **Statistiques :** Activer l’optimisation basée sur les stats de table

---

## 7. Annexes

### 7.1 Inventaire des Fichiers
```
projet-final/
├── DE1_Project_Notebook_EN.ipynb          (Notebook principal)
├── de1_project_config.yml                 (Configuration)
├── DE1_Project_Report.md                  (Ce document)
├── project_genai.md                       (Usage GenAI)
├── outputs/
│   └── project/
│       ├── bronze/                        (CSV brut)
│       ├── silver/                        (Parquet nettoyé)
│       ├── silver_optimized/              (Parquet partitionné)
│       └── gold/                          (Tables analytiques)
│           ├── q1_daily_aggregation/
│           ├── q2_top_referrers/
│           └── q3_filtered_analysis/
└── proof/
  ├── baseline_q1_plan.txt               (Plan physique Q1)
  ├── baseline_q2_plan.txt               (Plan physique Q2)
  ├── baseline_q3_plan.txt               (Plan physique Q3)
  ├── optimized_q1_plan.txt              (Plan optimisé Q1)
  ├── optimized_q2_plan.txt              (Plan optimisé Q2)
  ├── optimized_q3_plan.txt              (Plan optimisé Q3)
  ├── metrics7.png                       (Métriques)
  ├── metrics8.png                       (Métriques)
  ├── metrics9.png                       (Métriques)
  ├── metrics_10.png                     (Métriques)
  ├── metrics_11.png                     (Métriques)
  ├── metrics_13.png                     (Métriques)
  ├── metrics_15.png                     (Métriques)
  ├── metrics12.png                      (Métriques)
  ├── Sparkjob.png                       (Capture Spark)
```

### 7.2 Extraits de Configuration
```yaml
slo:
  freshness_hours: 2
  q1_latency_p95_seconds: 4
  storage_ratio_max: 0.60

layout:
  partition_by: []
  sort_by: []
  target_file_size_mb: 128

queries:
  q1: "Top 20 pages les plus visitées"
  q2: "Top 20 pages référentes"
  q3: "Analyse des clics par type"
```


### 7.3 Références
- Documentation Apache Spark : https://spark.apache.org/docs/latest/
- Spécification Parquet : https://parquet.apache.org/docs/
- Supports de cours DE1  de Bard TAJINI: ESIEE 2025-2026

**Remise :** Voir `project_genai.md` pour la déclaration d’usage d’IA
