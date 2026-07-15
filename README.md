# Agent IA de Statistiques Régionales — Sénégal

Agent conversationnel Django capable de répondre en français à des questions sur des indicateurs régionaux du Sénégal.

## ⚠️ Avertissement Important

**Les données utilisées dans cette application sont strictement pédagogiques et fictives.** Elles imitent la structure de données d'une agence comme l'ANSD mais ne contiennent aucune donnée officielle.

## 📋 Description

L'application permet de poser des questions en langage naturel sur 9 indicateurs statistiques pour les 14 régions du Sénégal sur la période 2020-2024 :

- Population
- Taux d'urbanisation
- Taux d'alphabétisation
- Taux de chômage
- Taux de pauvreté
- Accès à Internet
- Nombre de centres de santé
- Taux de scolarisation
- Production céréalière

## 🚀 Installation

### Prérequis

- Python 3.11+
- pip

### Configuration

1. Créer un environnement virtuel :
```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Appliquer les migrations :
```bash
python manage.py migrate
```

4. Importer les données fictives :
```bash
python manage.py importer_statistiques donnees-statistiques-senegal-fictives.csv
```

5. Lancer le serveur :
```bash
python manage.py runserver
```

6. Ouvrir http://127.0.0.1:8000/ dans votre navigateur

## 📊 Exemples de questions

### Questions simples (value)
- "Quel est le taux de chômage à Dakar en 2024 ?"
- "Population de Thiès en 2023"
- "Combien de centres de santé à Saint-Louis ?"

### Comparaisons (compare)
- "Compare l'accès à Internet entre Dakar et Thiès en 2024"
- "Compare le taux de pauvreté entre Dakar, Diourbel et Kolda"

### Évolutions (trend)
- "Évolution de la population à Saint-Louis entre 2020 et 2024"
- "Tendance du taux de chômage à Dakar de 2020 à 2024"

### Classements (ranking)
- "Classement des régions par taux de scolarisation en 2024"
- "Top 5 des régions par accès à Internet"

### Agrégations (sum/average)
- "Total de la population en 2024"
- "Moyenne du taux de pauvreté en 2024"

## 🧪 Tests

Exécuter tous les tests :
```bash
python manage.py test statistiques
```

Exécuter des tests spécifiques :
```bash
python manage.py test statistiques.tests_import
python manage.py test statistiques.tests_api
python manage.py test statistiques.tests_analyseur
python manage.py test statistiques.tests_moteur
```

## 📁 Structure du projet

```
agent_ia_senegal/
├── senegal_agent_ia/          # Configuration Django
│   ├── settings.py
│   └── urls.py
├── statistiques/              # Application principale
│   ├── models.py             # Modèle StatistiqueRegionale
│   ├── analyseur.py          # Analyseur de questions (NLU)
│   ├── moteur.py             # Moteur de requêtes ORM
│   ├── views.py              # API et vues
│   ├── admin.py              # Interface d'administration
│   ├── Templates/
│   │   ├── base.html         # Template de base
│   │   └── interface.html    # Interface conversationnelle
│   ├── management/commands/
│   │   └── importer_statistiques.py
│   └── tests_*.py            # Tests automatisés
├── manage.py
├── requirements.txt
└── README.md
```

## 🔒 Sécurité

- **Aucun SQL brut généré** : toutes les requêtes utilisent exclusivement l'ORM Django
- **Listes blanches** : tous les noms de champs sont validés contre des listes blanches codées en dur
- **Validation stricte** : les entrées utilisateur sont analysées et validées avant exécution
- **Pas de SQL injection** : impossible d'injecter du SQL via les questions

## 🎯 Fonctionnalités

### Analyseur de questions
- Détection des indicateurs par alias français
- Reconnaissance des 14 régions (insensible à la casse/accents)
- Extraction des années (2020-2024)
- Détection de 6 opérations : value, compare, trend, ranking, sum, average
- Gestion des cas ambigus et hors sujet

### Moteur ORM
- 6 opérations supportées avec l'ORM Django
- Association automatique des types de graphiques (bar/line)
- Réponses structurées en JSON stable
- Gestion des cas sans données

### Interface web
- Formulaire de question avec exemples cliquables
- Affichage de la réponse textuelle
- Tableau de données
- Graphiques interactifs (Chart.js)
- Design responsive et moderne

### API REST
- Endpoint : `POST /api/question/`
- Format d'entrée : `{"question": "..."}`
- Format de sortie : `{answer, table, chart, metadata}`

## 📝 Commandes d'import

La commande d'import valide :
- ✓ Colonnes obligatoires présentes
- ✓ Régions dans la liste des 14 régions du Sénégal
- ✓ Années entre 2020 et 2024
- ✓ Pourcentages entre 0 et 100
- ✓ Import idempotent (pas de doublon au 2e import)

## ⚙️ Interface d'administration

Accès : http://127.0.0.1:8000/admin/

Créer un superutilisateur :
```bash
python manage.py createsuperuser
```

## 🔍 Limites et améliorations possibles

### Limites actuelles
- Données fictives uniquement (70 observations)
- Période limitée à 2020-2024
- Questions en français uniquement
- Pas de persistance de l'historique des conversations
- Pas d'authentification utilisateur

### Améliorations possibles
- Ajouter plus d'indicateurs et de régions
- Supporter plusieurs langues (wolof, anglais)
- Ajouter un historique de conversation persistant
- Intégrer un LLM pour reformuler les réponses
- Ajouter des exports PDF/Excel
- Créer un dashboard avec visualisations avancées
- Développer l'application mobile Flutter
- Ajouter des alertes sur les tendances

## 👥 Contributeurs

- **Amsatou Ndiaye** : Analyseur de questions + Moteur ORM
- **Amy Ndiaye** : Import CSV + API + Interface + Tests

## 📄 Licence

Projet pédagogique — Données fictives uniquement
