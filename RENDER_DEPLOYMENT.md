# Déploiement du Backend Django sur Render

## Étapes pour déployer l'API Django sur Render

### 1. Prérequis

- Un compte Render (https://render.com)
- Un compte GitHub avec le repository du projet
- Les modifications de configuration déjà appliquées (voir fichiers modifiés ci-dessous)

### 2. Fichiers de configuration modifiés/créés

**Fichiers modifiés:**
- `requirements.txt` - Ajouté gunicorn, psycopg2-binary, dj-database-url
- `senegal_agent_ia/settings.py` - Configuration PostgreSQL, CORS, static files

**Fichiers créés:**
- `render.yaml` - Configuration Render pour le déploiement automatique

### 3. Étapes de déploiement

#### Étape 1: Connecter GitHub à Render

1. Connectez-vous sur https://render.com
2. Allez dans "Dashboard" → "New" → "Web Service"
3. Connectez votre compte GitHub si ce n'est pas déjà fait
4. Sélectionnez le repository `Amsatou2603/AI-Agent`

#### Étape 2: Configuration du Web Service

Render détectera automatiquement le fichier `render.yaml` et pré-remplira la configuration:

**Configuration automatique via render.yaml:**
- **Name**: senegal-agent-ia-api
- **Runtime**: Python
- **Build Command**: pip install -r requirements.txt && python manage.py collectstatic --noinput
- **Start Command**: gunicorn senegal_agent_ia.wsgi:application
- **Database**: PostgreSQL (créé automatiquement)

**Variables d'environnement (automatiques):**
- `SECRET_KEY`: Généré automatiquement
- `DEBUG`: False
- `ALLOWED_HOSTS`: .onrender.com
- `DATABASE_URL`: Connecté à la base PostgreSQL
- `PYTHON_VERSION`: 3.11.4
- `CORS_ALLOWED_ORIGINS`: À personnaliser avec votre URL Flutter

#### Étape 3: Personnaliser CORS_ALLOWED_ORIGINS

Après le déploiement initial, vous devez mettre à jour cette variable avec l'URL de votre application Flutter:

1. Allez dans votre service sur Render
2. Cliquez sur "Environment"
3. Modifiez `CORS_ALLOWED_ORIGINS` avec l'URL de votre app Flutter:
   - Si Flutter sur Vercel: `https://votre-app.vercel.app`
   - Si Flutter sur Render: `https://votre-app.onrender.com`
   - Vous pouvez mettre plusieurs URLs séparées par des virgules

#### Étape 4: Déployer

1. Cliquez sur "Create Web Service"
2. Render va automatiquement:
   - Créer une base PostgreSQL
   - Installer les dépendances
   - Exécuter les migrations
   - Collecter les fichiers statiques
   - Démarrer le serveur gunicorn

3. Attendez que le déploiement soit terminé (quelques minutes)

#### Étape 5: Vérifier le déploiement

1. Une fois terminé, Render vous donnera une URL comme: `https://senegal-agent-ia-api.onrender.com`
2. Testez l'endpoint: `https://senegal-agent-ia-api.onrender.com/api/question/`
3. Vérifiez les logs dans le dashboard Render si nécessaire

### 4. Migrations de base de données

Les migrations doivent s'exécuter automatiquement. Si ce n'est pas le cas, ajoutez cette commande au buildCommand dans render.yaml:

```yaml
buildCommand: pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
```

### 5. Mettre à jour l'URL de l'API dans Flutter

Après avoir obtenu l'URL Render, mettez-la dans votre configuration Flutter:

**Pour Docker:**
```bash
# Dans .env ou docker-compose.yml
API_URL=https://senegal-agent-ia-api.onrender.com
```

**Pour Vercel:**
```json
// Dans vercel.json
{
  "buildCommand": "flutter build web --release --dart-define=API_URL=https://senegal-agent-ia-api.onrender.com",
  ...
}
```

### 6. Surveillance et logs

- **Logs**: Disponibles dans le dashboard Render → Logs
- **Métriques**: Disponibles dans Metrics
- **Redéploiement**: Automatique à chaque push sur GitHub

### 7. Dépannage

**Erreur de connexion à la base de données:**
- Vérifiez que `DATABASE_URL` est correctement configuré
- Vérifiez les logs Render

**Erreur CORS:**
- Vérifiez que `CORS_ALLOWED_ORIGINS` contient votre URL Flutter
- Vérifiez que `DEBUG=False` en production

**Erreur 500:**
- Vérifiez les logs Render pour les détails
- Assurez-vous que toutes les migrations sont appliquées

### 8. Variables d'environnement supplémentaires

Si vous utilisez un LLM externe, ajoutez ces variables dans Render:

- `LLM_API_KEY`: Votre clé API
- `LLM_API_URL`: URL de l'API LLM

### 9. Domaine personnalisé (optionnel)

Pour utiliser un domaine personnalisé:

1. Allez dans Settings → Custom Domains
2. Ajoutez votre domaine
3. Configurez les DNS selon les instructions Render

### 10. Sécurité

- `DEBUG=False` est activé par défaut
- `SECRET_KEY` est généré automatiquement
- `ALLOWED_HOSTS` est limité aux domaines Render
- CORS est configuré pour les origines autorisées uniquement
