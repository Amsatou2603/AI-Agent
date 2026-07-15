# Docker Deployment - Agent IA Flutter

## Configuration Docker pour le déploiement de l'application Flutter Web

Cette configuration Docker utilise une approche multi-stage pour construire l'application Flutter et la servir avec nginx.

## Fichiers créés

- `Dockerfile`: Configuration multi-stage pour le build Flutter et nginx
- `nginx.conf`: Configuration nginx optimisée pour Flutter Web
- `docker-compose.yml`: Configuration pour faciliter le déploiement
- `.dockerignore`: Fichiers à exclure du contexte Docker

## Prérequis

- Docker installé sur votre machine
- Docker Compose (optionnel, mais recommandé)

## Instructions de déploiement

### 1. Configurer l'URL de l'API

Avant de construire l'image, définissez l'URL de votre API Django:

**Avec docker-compose:**
```bash
# Créer un fichier .env
API_URL=https://votre-api-django.com
```

**Ou passez-la directement lors du build:**
```bash
docker build --build-arg API_URL=https://votre-api-django.com -t agent-ia-flutter .
```

### 2. Construire et lancer avec Docker Compose (recommandé)

```bash
# Construire et démarrer le conteneur
docker-compose up -d --build

# Voir les logs
docker-compose logs -f

# Arrêter le conteneur
docker-compose down
```

L'application sera accessible sur `http://localhost:8080`

### 3. Construire et lancer avec Docker directement

```bash
# Construire l'image
docker build --build-arg API_URL=https://votre-api-django.com -t agent-ia-flutter .

# Lancer le conteneur
docker run -d -p 8080:80 --name agent-ia-flutter agent-ia-flutter

# Voir les logs
docker logs -f agent-ia-flutter

# Arrêter le conteneur
docker stop agent-ia-flutter
docker rm agent-ia-flutter
```

## Déploiement sur des plateformes cloud

### Docker Hub

```bash
# Tagger l'image
docker tag agent-ia-flutter votre-dockerhub-username/agent-ia-flutter:latest

# Push vers Docker Hub
docker push votre-dockerhub-username/agent-ia-flutter:latest
```

### AWS ECS / Google Cloud Run / Azure Container Instances

Utilisez l'image construite localement ou depuis Docker Hub et déployez selon la documentation de votre plateforme.

## Configuration nginx

Le fichier `nginx.conf` inclut:

- Compression gzip pour les fichiers statiques
- Headers de sécurité
- Gestion des routes Flutter (SPA)
- Cache pour les assets statiques (1 an)
- Configuration spéciale pour CanvasKit et Service Worker

## Variables d'environnement

- `API_URL`: URL de l'API Django (défaut: `https://votre-api-django.com`)

## Ports

- `8080`: Port externe (configurable dans docker-compose.yml)
- `80`: Port interne dans le conteneur nginx

## Dépannage

### Le conteneur ne démarre pas

```bash
# Voir les logs
docker-compose logs

# Vérifier si le port est déjà utilisé
netstat -ano | findstr :8080
```

### L'API ne répond pas

Vérifiez que l'URL de l'API est correctement configurée et accessible depuis le conteneur.

### Build lent

Le premier build peut prendre plusieurs minutes car Flutter doit être téléchargé. Les builds suivants seront plus rapides grâce au cache Docker.
