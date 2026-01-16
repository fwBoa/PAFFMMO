# PAFFMMO - Système de Gestion et Atlas Interactif RPG

**Auteur:** Jean-David ZamBLEZIE
**Sujet:** Système de gestion et atlas interactif pour l'univers RPG "PAFFMMO"

## Architecture

- **Backend:** Django + Django Rest Framework
- **Base de données:** Oracle Database (via Docker)
- **Frontend:** Vue.js + NES.css (style 8-bit)
- **Infrastructure:** Docker & Docker Compose

## Tables de Données

### Hero (Héros)
- `id`, `nickname`, `job_class`, `level`, `hp_current`, `xp`, `gold`, `is_active`, `biography`, `created_at`
- Relations: ManyToMany avec Skills, ForeignKey vers Region

### Region (Région)
- `id`, `name`, `environment_type`
- Relation: OneToMany avec Hero

### Skill (Compétence)
- `id`, `name`, `damage_type`, `mana_cost`
- Relation: ManyToMany avec Hero

## Lancement du Projet

```bash
# Cloner le projet
git clone <repository-url>
cd PAFFMMO

# Lancer avec Docker Compose
docker-compose up --build

# Ou en mode développement sans Oracle (SQLite)
docker-compose up --build -f docker-compose.dev.yml
```

## Services Disponibles

- **Application:** http://localhost:8000
- **Admin Django:** http://localhost:8000/admin
- **API REST:** http://localhost:8000/api/

## Commandes Utiles

### Création du super-utilisateur
```bash
docker-compose exec web python manage.py createsuperuser
```

### Génération de données aléatoires
```bash
docker-compose exec web python manage.py generate_data
docker-compose exec web python manage.py generate_data --heroes=200
docker-compose exec web python manage.py generate_data --clear
```

### Commandes Django supplémentaires
```bash
# Appliquer les migrations
docker-compose exec web python manage.py migrate

# Collecter les fichiers statiques
docker-compose exec web python manage.py collectstatic

# Créer un super-utilisateur avec nom d'utilisateur
docker-compose exec web python manage.py createsuperuser --username=admin
```

## Fonctionnalités Admin

- **Export PDF:** Génération de fiche de personnage
- **Graphiques:** Dashboard avec Matplotlib (répartition des classes, niveaux par région)
- **Export CSV/Excel:** Téléchargement des données
- **Faker:** Script de génération de 100+ héros cohérents

## Fonctionnalités API REST

```
GET /api/heroes/          # Liste des héros (paginé, filtrable)
GET /api/heroes/{id}/     # Détail d'un héros
GET /api/regions/         # Liste des régions
GET /api/skills/          # Liste des compétences
GET /api/stats/           # Statistiques globales
```

Paramètres de filtrage:
- `search`: Recherche dans nom, classe, biographie
- `job_class`: Filtrer par classe
- `ordering`: Trier par level, created_at, gold

## Dépannage

### Oracle Database ne démarre pas
```bash
docker-compose down -v
docker-compose up -d
```

### Réinitialiser la base de données
```bash
docker-compose down -v
docker-compose up --build
```

### Voir les logs
```bash
docker-compose logs -f web
docker-compose logs -f db
```

## Licence

MIT
