# Agent IA Sénégal - Application Flutter

Application mobile pour interroger les statistiques régionales du Sénégal (2020-2024).

## ⚠️ Avertissement

Les données utilisées sont strictement pédagogiques et fictives. Aucune donnée officielle de l'ANSD.

## 🎨 Design

Interface moderne style Apple 2026 avec :
- Palette de couleurs Apple (bleu, vert, orange, etc.)
- Animations fluides et transitions douces
- Graphiques interactifs (barres et lignes)
- Design responsive et épuré

## 🚀 Installation

### Prérequis
- Flutter SDK (3.11.4+)
- Dart SDK
- Android Studio ou Xcode

### Configuration

1. Installer les dépendances :
```bash
cd agent_ia_flutter
flutter pub get
```

2. Configurer l'URL de l'API :

Modifier `lib/services/api_service.dart` :
```dart
static const String baseUrl = 'http://10.0.2.2:8000';  // Pour émulateur Android
// ou
static const String baseUrl = 'http://localhost:8000';  // Pour iOS simulator
// ou
static const String baseUrl = 'http://192.168.1.X:8000';  // Pour device physique
```

3. Démarrer le serveur Django :
```bash
cd ../
python manage.py runserver 0.0.0.0:8000
```

4. Lancer l'app Flutter :
```bash
cd agent_ia_flutter
flutter run
```

## 📱 Fonctionnalités

### Interface conversationnelle
- Saisie de questions en langage naturel
- Exemples de questions cliquables
- Historique de conversation

### Affichage des réponses
- Réponse textuelle formatée
- Tableau de données interactif
- Graphiques (barres et lignes) avec fl_chart

### Design Apple 2026
- Couleurs modernes et vibrantes
- Typographie SF Pro
- Animations fluides
- Graphiques style Apple avec coins arrondis
- Points interactifs sur les lignes
- Tooltips élégants

## 📦 Dépendances

```yaml
http: ^1.2.0          # Client HTTP
fl_chart: ^0.69.0     # Graphiques
provider: ^6.1.1      # State management (si extensions futures)
```

## 🎯 Exemples de questions

- "Quel est le taux de chômage à Dakar en 2024 ?"
- "Compare l'accès à Internet entre Dakar et Thiès en 2024"
- "Évolution de la population à Saint-Louis entre 2020 et 2024"
- "Classement des régions par taux de scolarisation en 2024"
- "Moyenne du taux de pauvreté en 2024"

## 🏗️ Architecture

```
lib/
├── main.dart                      # Point d'entrée
├── models/
│   └── query_response.dart        # Modèles de données
├── services/
│   └── api_service.dart           # Service API HTTP
├── theme/
│   └── app_theme.dart             # Thème Apple 2026
├── screens/
│   └── home_screen.dart           # Écran principal
└── widgets/
    ├── chat_message_widget.dart   # Widget message
    ├── data_table_widget.dart     # Widget tableau
    └── chart_widget.dart          # Widget graphique
```

## 🔧 Résolution des problèmes

### Erreur de connexion
- Vérifier que le serveur Django est démarré
- Vérifier l'URL dans `api_service.dart`
- Pour device physique : utiliser l'IP locale du PC

### Graphiques ne s'affichent pas
- Vérifier que `fl_chart` est bien installé : `flutter pub get`
- Redémarrer l'app en mode debug

### Problèmes de build
```bash
flutter clean
flutter pub get
flutter run
```

## 🎨 Couleurs Apple utilisées

- Bleu Apple: #007AFF
- Vert: #34C759
- Orange: #FF9500
- Rouge: #FF3B30
- Violet: #AF52DE
- Jaune: #FFCC00
- Cyan: #5AC8FA
- Rose: #FF2D55

## 📄 Licence

Projet pédagogique — Données fictives uniquement
