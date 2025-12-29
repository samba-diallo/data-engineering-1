# Documentation d’Utilisation de l’IA Générative
**Projet :** Projet Final DE1 - Lakehouse Local  
**Auteurs :** DIALLO Samba & DIOP Mouhamed  
**Date :** Décembre 2025  

---

## 1. Déclaration

Ce document décrit comment les outils d’IA générative ont été utilisés (ou non) pour la réalisation de ce projet final de Data Engineering I.

---

## 2. Outils d’IA Utilisés

### 2.1 GitHub Copilot (Extension VS Code)
**But :** Assistance au code et génération de structure de projet  
**Niveau d’utilisation :** Étendu  

#### Cas d’Usage Spécifiques :
1. **Mise en place de la structure du projet**
   - Génération de l’arborescence initiale pour les couches lakehouse (bronze/silver/gold)
   - Création du fichier `de1_project_config.yml` complet avec toutes les sections requises
   - Génération des cellules de notebook avec titres markdown adaptés

2. **Génération de code**
   - Transformations PySpark DataFrame pour la couche silver (application du schéma, conversions de type)
   - Logique de validation qualité à partir des règles de config
   - Capture des plans physiques et opérations de fichiers
   - Code de journalisation des métriques et validation SLO

3. **Documentation**
   - Génération du modèle de rapport avec structure académique
   - Création de commentaires de code expliquant les stratégies d’optimisation
   - Rédaction de cette documentation d’usage GenAI

#### Ce qui N’a PAS été Généré :
- **Décisions métier :** Les requêtes (Q1-Q3) ont été conçues manuellement à partir de l’analyse du jeu de données Wikipedia clickstream
- **Cibles SLO :** Les objectifs (latence 4s, stockage 60%) ont été fixés selon les exigences du projet et la contrainte 16Go RAM
- **Stratégie d’optimisation :** Les choix de repartitionnement et tri ont été faits après analyse manuelle des performances
- **Interprétation des métriques :** L’analyse des performances (19,4s vs 0,5s) a été réalisée manuellement via Spark UI

---

## 3. Contributions Humaines

### 3.1 Décisions de Conception
Toutes les décisions d’architecture ont été prises manuellement :
- **Choix du dataset :** Wikipedia Clickstream Novembre 2024 pour sa taille (10M lignes, 450Mo) et sa pertinence analytique
- **Stratégie d’optimisation :** Repartitionnement + tri par nombre de clics (n DESC) après analyse des requêtes
- **Ordre de tri :** sortWithinPartitions par n décroissant pour optimiser les requêtes TOP-N
- **Taille des fichiers :** Calcul de 128Mo cible selon la RAM et le parallélisme
- **Tuning mémoire :** driver.memory=4g, executor.memory=4g après avertissements de cache

### 3.2 Tests et Validation
- **Exécution notebook :** Toutes les cellules ont été exécutées manuellement pour valider la justesse
- **Débogage :** Correction manuelle des erreurs de schéma et de qualité
- **Mesure de performance :** Capture manuelle des métriques Spark UI pour chaque requête
- **Validation SLO :** Comparaison manuelle des métriques base/optimisé avec les cibles

### 3.3 Esprit Critique
- **Justification des optimisations :** Analyse des plans physiques pour comprendre les gains
- **Analyse des compromis :** Évaluation du nombre de partitions vs taille de fichier
- **Identification des limites :** Reconnaissance des contraintes monoposte et documentation des solutions

---

## 4. Méthodologie d’Interaction avec l’IA

### 4.1 Stratégie de Prompt
Utilisation de prompts précis et contextualisés :
```
Exemple : « Crée du code PySpark pour appliquer un schéma depuis un YAML,
           appliquer les règles qualité, et journaliser les violations sans emojis »
```

### 4.2 Revue de Code
Chaque code généré par l’IA a été :
1. **Relu :** Vérifié pour la justesse et les bonnes pratiques PySpark
2. **Testé :** Exécuté dans le notebook pour valider la fonctionnalité
3. **Adapté :** Modifié pour correspondre au schéma réel et aux besoins
4. **Documenté :** Commenté pour expliquer la logique

### 4.3 Limites Rencontrées
- **Schémas génériques :** L’IA proposait des schémas à adapter manuellement
- **Spécificité des requêtes :** Les requêtes exactes ont été réécrites à la main
- **Collecte des métriques :** L’IA proposait des modèles mais ne pouvait accéder à Spark UI ; métriques remplies manuellement

---

## 5. Compétences Développées

### 5.1 Compétences grâce à l’IA
- **Prototypage rapide :** Structure générée rapidement puis raffinée manuellement
- **Patterns de code :** Apprentissage d’idiomes PySpark via suggestions IA (ex : `sortWithinPartitions`)
- **Standards de documentation :** Les modèles IA ont montré une structure professionnelle

### 5.2 Compétences Développées en Autonomie
- **Analyse de performance :** Lecture des plans physiques Spark et métriques UI
- **Techniques d’optimisation :** Compréhension du partition pruning, sizing, AQE par expérimentation
- **Conception système :** Architecture lakehouse selon les principes du cours DE1

---

## 6. Considérations Éthiques

### 6.1 Intégrité Académique
- **Pas de plagiat :** Tout code IA relu, compris et adapté
- **Attribution claire :** Ce document déclare explicitement l’usage de l’IA
- **Travail original :** Les choix, analyses et conclusions sont originaux

### 6.2 Respect de la Politique de Collaboration
Ce projet respecte la politique ESIEE sur l’usage de l’IA :
- IA utilisée comme **outil de productivité**, pas comme substitut à l’apprentissage
- Tout le travail a été **validé et compris** avant soumission
- **Esprit critique** appliqué à chaque suggestion IA

---

## 7. Conclusion

**Rôle de l’IA :** Accélérateur et générateur de structure  
**Rôle humain :** Concepteur, analyste, validateur, esprit critique  

L’IA générative a permis un gain de temps significatif (environ 40% sur le code standard), mais toutes les décisions d’ingénierie, analyses de performance et stratégies d’optimisation sont restées humaines. Ce projet illustre une collaboration IA-humain efficace dans le respect de l’intégrité académique et de la compréhension technique.

---

## 8. Annexe : Pourcentage de Code Généré par l’IA

| Composant | Généré IA | Écrit humain | Adapté humain |
|-----------|-----------|--------------|---------------|
| YAML config | 80% | 20% | 0% |
| Notebook (bronze) | 60% | 20% | 20% |
| Notebook (silver) | 50% | 30% | 20% |
| Notebook (gold) | 40% | 40% | 20% |
| Code optimisation | 30% | 50% | 20% |
| Rédaction rapport | 70% | 20% | 10% |
| Doc GenAI | 60% | 40% | 0% |

**Estimation globale :** 55% structure IA, 30% travail original, 15% adaptation humaine

---

**Signature :** DIALLO Samba & DIOP Mouhamed  
**Date :** [Date de soumission]  
**Affirmation :** Nous affirmons que ce document reflète fidèlement l’usage de l’IA générative dans ce projet.
