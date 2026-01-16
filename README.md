# PAFFMMO - Système de Gestion et Atlas Interactif RPG

**Auteur:** Jean-David ZamBLEZIE  
**Version:** 2.0.0 (Django 6.0)  
**Dernière mise à jour:** Janvier 2026

## 🏗️ Architecture

| Composant | Technologie | Version |
|-----------|-------------|---------|
| **Backend** | Django + Django Rest Framework | 6.0 / 3.15 |
| **Base de données** | Oracle Database (prod) / SQLite (dev) | - |
| **Frontend** | Vue.js + NES.css (style 8-bit) | 3.x |
| **Python** | Python | 3.12+ |
| **Infrastructure** | Docker & Docker Compose | - |

## 📋 Prérequis

- **Python 3.12+** (requis par Django 6.0)
- **Docker & Docker Compose** (recommandé)
- **Node.js** (optionnel, pour le développement frontend)

## 🗃️ Modèles de Données

### Hero (Héros)
| Champ | Type | Description |
|-------|------|-------------|
| `nickname` | CharField | Nom unique du héros |
| `job_class` | CharField | Classe (Guerrier, Mage, etc.) |
| `level` | PositiveIntegerField | Niveau (1 par défaut) |
| `hp_current` | PositiveIntegerField | Points de vie actuels |
| `xp` | PositiveIntegerField | Expérience |
| `gold` | PositiveIntegerField | Or |
| `is_active` | BooleanField | Statut actif |
| `biography` | TextField | Biographie |
| `region` | ForeignKey → Region | Région actuelle |
| `skills` | ManyToMany → Skill | Compétences |

### Region (Région)
- `name` : Nom unique de la région
- `environment_type` : Type d'environnement

### Skill (Compétence)
- `name` : Nom de la compétence
- `damage_type` : Type (physical, magical, healing, mixed)
- `mana_cost` : Coût en mana

## 🚀 Lancement du Projet

### Option 1 : Docker Compose (Recommandé)

```bash
# Cloner le projet
git clone <repository-url>
cd PAFFMMO

# Mode développement (SQLite)
docker-compose -f docker-compose.dev.yml up --build

# Mode production (Oracle)
docker-compose up --build
```

### Option 2 : Installation Locale

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou: venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate

# Générer des données de test
python manage.py generate_data --heroes=100

# Créer un super-utilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

## 🌐 Services Disponibles

| Service | URL | Description |
|---------|-----|-------------|
| **Application** | http://localhost:8000 | Atlas interactif |
| **Admin Django** | http://localhost:8000/admin | Interface d'administration |
| **API REST** | http://localhost:8000/api/ | Endpoints JSON |

## 📡 API REST

### Endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/heroes/` | GET | Liste paginée des héros |
| `/api/heroes/{id}/` | GET | Détail d'un héros |
| `/api/heroes/by_class/?class=warrior` | GET | Filtrer par classe |
| `/api/heroes/stats/` | GET | Statistiques globales |
| `/api/heroes/top/?limit=10` | GET | Top héros par niveau |
| `/api/regions/` | GET | Liste des régions |
| `/api/skills/` | GET | Liste des compétences |

### Paramètres de Requête

| Paramètre | Description | Exemple |
|-----------|-------------|---------|
| `search` | Recherche texte | `?search=dragon` |
| `job_class` | Filtrer par classe | `?job_class=mage` |
| `is_active` | Filtrer par statut | `?is_active=true` |
| `region` | Filtrer par région (ID) | `?region=1` |
| `min_level` | Niveau minimum | `?min_level=10` |
| `max_level` | Niveau maximum | `?max_level=50` |
| `ordering` | Tri | `?ordering=-level,gold` |
| `page` | Pagination | `?page=2` |

### Exemple de Réponse

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/heroes/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "nickname": "DragonSlayer42",
      "job_class": "warrior",
      "job_class_display": "Guerrier",
      "level": 45,
      "hp_current": 4200,
      "max_hp": 4500,
      "hp_percentage": 93.3,
      "xp": 125000,
      "gold": 3500,
      "is_active": true,
      "region": 1,
      "region_name": "Royaume d'Eldoria",
      "created_at": "2026-01-15T10:30:00Z"
    }
  ]
}
```

## 🛠️ Commandes Utiles

### Gestion des Données

```bash
# Générer 100 héros
docker-compose exec web python manage.py generate_data --heroes=100

# Générer 200 héros
docker-compose exec web python manage.py generate_data --heroes=200

# Effacer et régénérer
docker-compose exec web python manage.py generate_data --clear --heroes=100
```

### Django

```bash
# Appliquer les migrations
docker-compose exec web python manage.py migrate

# Créer une nouvelle migration
docker-compose exec web python manage.py makemigrations

# Collecter les fichiers statiques
docker-compose exec web python manage.py collectstatic --noinput

# Shell Django
docker-compose exec web python manage.py shell
```

## 🎨 Fonctionnalités Admin

- **📊 Dashboard** : Graphiques Matplotlib (répartition classes, niveaux par région)
- **📄 Export PDF** : Génération de fiches personnage professionnelles
- **📑 Export CSV/Excel** : Téléchargement des données
- **🎲 Faker** : Génération automatique de héros cohérents

## 🔧 Variables d'Environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `DJANGO_SECRET_KEY` | Clé secrète Django | (dev key) |
| `DJANGO_DEBUG` | Mode debug | `True` |
| `DJANGO_ALLOWED_HOSTS` | Hosts autorisés | `*` |
| `DATABASE_ENGINE` | Engine DB (`sqlite3` ou `oracle`) | `sqlite3` |
| `DATABASE_NAME` | Nom de la base | `db.sqlite3` |
| `DATABASE_USER` | Utilisateur Oracle | `system` |
| `DATABASE_PASSWORD` | Mot de passe Oracle | `oracle` |
| `DATABASE_HOST` | Hôte Oracle | `db` |
| `DATABASE_PORT` | Port Oracle | `1521` |

## 🐳 Docker

### Développement

```bash
docker-compose -f docker-compose.dev.yml up --build
```

### Production

```bash
docker-compose up --build -d
```

### Logs

```bash
docker-compose logs -f web
docker-compose logs -f db
```

### Réinitialisation

```bash
docker-compose down -v
docker-compose up --build
```

## 📁 Structure du Projet

```
PAFFMMO/
├── manage.py                    # Point d'entrée Django
├── requirements.txt             # Dépendances Python
├── Dockerfile                   # Image Docker (Python 3.12)
├── docker-compose.yml           # Production (Oracle)
├── docker-compose.dev.yml       # Développement (SQLite)
├── paffmmo_project/
│   ├── settings.py              # Configuration Django 6.0
│   ├── urls.py                  # Routes principales
│   └── wsgi.py                  # WSGI Application
├── rpgAtlas/
│   ├── models.py                # Modèles Hero, Region, Skill
│   ├── views.py                 # API ViewSets
│   ├── serializers.py           # DRF Serializers
│   ├── admin.py                 # Admin personnalisé
│   ├── urls.py                  # Routes API
│   ├── templates/
│   │   └── index.html           # Frontend Vue.js
│   └── management/commands/
│       └── generate_data.py     # Script Faker
└── img/
    └── image.png                # Banner PAFFMMO
```

## 🔄 Changelog

### v2.0.0 (Janvier 2026)
- ⬆️ Migration vers Django 6.0
- ⬆️ Python 3.12+ requis
- ✨ Nouveau système STORAGES (WhiteNoise)
- ✨ Variables d'environnement pour la configuration
- ✨ Logging configuré
- ✨ Index de base de données pour les performances
- ✨ Nouveaux endpoints API (top, stats améliorés)
- ✨ Cache sur les statistiques
- 🔒 Configuration CSRF renforcée

### v1.0.0
- 🎉 Version initiale avec Django 4.2

## 📄 Licence

MIT
