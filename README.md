# BI Analytics — Rapport Hebdomadaire

Pipeline Python automatisé de traitement et visualisation des données ADV et Service Client, avec dashboard interactif Streamlit.

---

## Présentation

Chaque semaine, deux services transmettent des fichiers Excel de suivi (J'ai adapté les noms pour faire simple):
- **Administration des Ventes (ADV)** -> 'suivi_commandes_sXX.xlsx'
- **Service Client** → `suivi_chantiersCT_sXX.xlsx`

Ce projet remplace l'analyse manuelle par un pipeline Python qui génère automatiquement des KPIs, des graphiques et un rapport Excel — en moins de 1 minute.

Le dashboard est accessible depuis un navigateur, sans installation, via Streamlit Cloud.

---

## Fonctionnalités

- Chargement et nettoyage automatique des fichiers Excel (en-têtes décalées, espaces parasites, colonnes vides)
- Calcul des KPIs hebdomadaires : CA HT/TTC, commandes bloquées, chantiers en retard, facturations partielles
- Requêtes SQL sur les données via SQLite (CA par service, commandes bloquées, jointures BC × factures)
- Dashboard interactif Streamlit avec upload des fichiers directement dans l'interface
- Export automatique : 2 graphiques PNG + 1 rapport Excel multi-onglets
- Pipeline en ligne de commande pour un usage local (`python main.py`)

---

## Structure du projet

```
bi-analytics/
├── app.py               # Dashboard Streamlit (interface web)
├── main.py              # Pipeline en ligne de commande
├── config.py            # Paramètres centralisés (semaine, chemins, feuilles)
├── requirements.txt     # Dépendances Python
├── .gitignore
├── src/
│   ├── extract.py       # Lecture et nettoyage des fichiers Excel
│   ├── transform.py     # Calcul des KPIs Pandas
│   ├── database.py      # Base SQLite et requêtes SQL
│   └── report.py        # Génération des graphiques et export Excel
├── data/
│   ├── raw/             # Fichiers Excel sources (non versionnés)
│   └── processed/       # Base SQLite générée automatiquement
├── notebooks/           # Exploration et tests Jupyter
└── output/              # Rapports générés (PNG, Excel)


---

## Installation locale

### Prérequis
- Python 3.11 ou supérieur
- Git

### Installation

'''bash
# Cloner le projet
git clone https://github.com/VOTRE_USERNAME/bi-analytics.git
cd bi-analytics

# Créer et activer l'environnement virtuel
python -m venv venv

# Windows
venv\Scripts\Activate.ps1

# Mac / Linux
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt


---

## Utilisation

### Option A - Pipeline ligne de commande (usage local)

'''bash
# 1. Déposer les fichiers Excel dans data/raw/
#    suivi_commandes_s12.xlsx
#    suivi_chantiersCT_s12.xlsx

# 2. Modifier la semaine dans config.py
SEMAINE = "s12"

# 3. Lancer le pipeline
python main.py


Résultat dans 'output/' :
- 'ca_service_s12.png' - graphique CA par service
- 'chantiers_s12.png' - graphique chantiers les moins avancés
- 'rapport_s12.xlsx' - rapport Excel avec onglets KPIs, CA Hebdo, Commandes bloquées

### Option B - Dashboard Streamlit (local)

'''bash
streamlit run app.py
# Ouvre automatiquement http://localhost:8501
'''

Déposez les deux fichiers Excel dans la barre latérale — le rapport se génère instantanément.

### Option C - Dashboard Streamlit Cloud (accès public)

Accessible via l'URL de déploiement sans installation.  
Uploadez les deux fichiers Excel directement dans l'interface.

---

## Fichiers attendus

| Fichier | Service émetteur | Feuilles utilisées |
|---|---|---|
| 'suivi_commandes_sXX.xlsx' | Administration des Ventes | Fsrs locaux, Fsrs Etrangers, BC Clients, CA Hebdo |
| 'suivi_chantiersCT_sXX.xlsx' | Service Client | Projet en cours 00-99%, Projet 100% Implémenté, T1 |

> Les fichiers portent un suffixe de semaine ('S11', 'S12'...) et sont transmis par mail chaque semaine.

---

## KPIs générés

| Indicateur | Source | Description |
|---|---|---|
| CA HT / TTC | CA Hebdo | Chiffre d'affaires total de la semaine |
| Commandes bloquées | Fsrs locaux + Etrangers | Commandes en attente de livraison, en traitement ou sous douane |
| Chantiers en retard | Projet en cours | Projets dont la date de fin estimée est dépassée et avancement < 100% |
| Facturations partielles | Projet 100% Implémenté | Projets livrés à 100% avec facturation incomplète — CA non encore encaissé |

---

## Architecture technique

```
Fichiers Excel (ADV + Service Client)
         │
         ▼
   src/extract.py        Lecture calamine + nettoyage Pandas
         │
         ▼
   src/transform.py      Calcul KPIs (groupby, filtres, agrégations)
         │
    ┌────┴────┐
    ▼         ▼
src/database.py     src/report.py
SQLite + SQL        Matplotlib + openpyxl
    │                    │
    ▼                    ▼
Tableaux SQL         PNG + Excel
    │
    ▼
  app.py (Streamlit) - Dashboard interactif
'''

---

## Dépendances

| Bibliothèque | Version | Usage |
|---|---|---|
| pandas | latest | Manipulation et analyse des données |
| python-calamine | latest | Lecture robuste des fichiers Excel |
| openpyxl | latest | Export Excel |
| streamlit | latest | Dashboard interactif |
| matplotlib | latest | Graphiques |

---

## Passer à la semaine suivante

La seule modification nécessaire chaque semaine :

'''python
# config.py
SEMAINE = "s12"  # ← changer ce numéro
'''

Puis déposer les nouveaux fichiers dans `data/raw/` et relancer `python main.py` ou rafraîchir le dashboard Streamlit.

---

## Auteur

Je l'ai développé dans le cadre d'un projet d'apprentissage BI Analytics — Python, Pandas, SQL, Streamlit.