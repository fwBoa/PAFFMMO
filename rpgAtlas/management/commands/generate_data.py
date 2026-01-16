"""
PAFFMMO - Script de génération de données
==========================================
Génère des héros, régions et compétences aléatoires via Faker.
Compatibilité Django 6.0+
"""
import random
from typing import List, Tuple

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from faker import Faker

from rpgAtlas.models import Hero, Region, Skill


# Configuration Faker avec locale française
fake = Faker(['fr_FR', 'en_US'])

# Classes de personnages disponibles
JOB_CLASSES = [choice[0] for choice in Hero.JobClass.choices]

# Données des régions : (nom, type d'environnement)
REGION_DATA: List[Tuple[str, str]] = [
    ("Royaume d'Eldoria", 'forest'),
    ('Montagnes de Fer', 'mountain'),
    ('Côtes des Tempêtes', 'coastal'),
    ('Désert de Sable Rouge', 'desert'),
    ('Terres Gelées du Nord', 'snowy'),
    ('Vallée des Ombres', 'swamp'),
    ("Plaines de l'Aube", 'plains'),
    ('Forêt Mystique', 'forest'),
    ('Volcan de Feu Noir', 'volcanic'),
    ('Îles Perdues', 'island'),
    ('Cité Flottante', 'sky'),
    ('Abysses Profondes', 'underwater'),
]

# Données des compétences : (nom, type de dégâts, coût mana)
SKILL_DATA: List[Tuple[str, str, int]] = [
    ('Coup Puissant', 'physical', 10),
    ('Boule de Feu', 'magical', 25),
    ('Tir Précis', 'physical', 15),
    ('Assassinat', 'physical', 30),
    ('Bouclier Sacré', 'healing', 20),
    ('Soin Majeur', 'healing', 15),
    ('Malédiction', 'magical', 35),
    ('Rugissement', 'physical', 20),
    ('Foudre', 'magical', 30),
    ('Poison Mortel', 'mixed', 25),
    ('Blizzard', 'magical', 28),
    ('Prière Divine', 'healing', 10),
    ('Faim du Loup', 'physical', 22),
    ('Tentacules Sombres', 'magical', 40),
    ('Masse Divine', 'physical', 45),
    ('Drain de Vie', 'mixed', 35),
    ('Téléportation', 'magical', 50),
    ('Régénération', 'healing', 30),
    ('Frappe Élémentaire', 'mixed', 20),
    ('Invocation', 'magical', 60),
]

# Templates de biographies
BIO_TEMPLATES: List[str] = [
    "Originaire de {origin}, {nickname} a quitté son village natal après une tragédie qui a décimé sa famille. Depuis, il parcourt le monde en quête de vengeance et de gloire.",
    "{nickname} est un héros légendaire dont les exploits sont chantés dans toutes les tavernes du royaume. On dit qu'il a vaincu le dragon noir à lui seul.",
    "Élevé par des moines guerriers, {nickname} a appris l'art du combat dès son plus jeune âge. Sa sagesse et sa force en font un allié précieux.",
    "Ancien mercenaire, {nickname} a laissé derrière lui un passé trouble. Aujourd'hui, il cherche la rédemption en aidant les plus faibles.",
    "{nickname} est né sous une lune rouge, ce qui lui confère des pouvoirs étranges. Les villageois le craignent, mais les monstres le redoutent encore plus.",
    "Chevalier sans maître, {nickname} erre à travers le royaume en quête d'honneur et de défis. Sa lame ne connaît pas la défaite.",
    "Magicien exilé de sa tour pour expériences interdites, {nickname} parcourt les terres sauvages en quête de connaissances perdues.",
    "{nickname} était autrefois un garde royal avant de découvrir la corruption au sein de la cour. Il a fui pour échapper au bûcher.",
    "Né dans les mines profondes, {nickname} a forgé sa propre destinée à coups de marteau et d'épée. Sa réputation le précède.",
    "{nickname} est un chasseur de primes intrépide. Sa cible actuelle : le seigneur noir qui terrorise la région.",
    "Orphelin élevé dans les rues, {nickname} a appris à survivre par la ruse et la vitesse. Personne ne l'attrape.",
    "Descendant d'une lignée de rois déchus, {nickname} porte le fardeau de restaurer la gloire de ses ancêtres.",
    "{nickname} a fait vœu de silence il y a des années. Seuls ses actes parlent pour lui, et ses actes sont éloquents.",
    "Guérisseur mystérieux, {nickname} apparaît là où le besoin se fait sentir. On murmure qu'il peut ramener les morts à la vie.",
    "{nickname} est un samouraï perdu dans ce monde étrange. Son code de l'honneur est inflexible, sa lame imparable.",
]

# Accroches pour enrichir les biographies
BIO_HOOKS: List[str] = [
    "On raconte qu'il a",
    "Sa réputation repose sur le fait qu'il a",
    "Les chroniques mentionnent qu'il a",
    "Les bardes chantent qu'il a",
    "Les rumeurs suggèrent qu'il a",
    "Les survivants témoignent qu'il a",
    "Les archives royales révèlent qu'il a",
    "Les anciennes légendes racontent qu'il a",
]

# Exploits héroïques
BIO_DEEDS: List[str] = [
    "vaincu un démon ancestral dans les profondeurs",
    "protégé le village pendant trois semaines sans repos",
    "trouvé le trésor perdu du roi maudit",
    "guéri la peste noire qui ravageait les campagnes",
    "défié l'empereur en combat singulier",
    "sauvé la princesse des griffes du dragon",
    "découvert un passage secret vers les souterrains",
    "apprivoisé une créature sauvage comme monture",
    "résolu l'énigme de la tour hantée",
    "rejeté l'offre du diable lui-même",
    "survécu à l'épreuve des sept mers",
    "détruit l'artefact maudit qui corrompait la terre",
]


class Command(BaseCommand):
    """Commande Django pour générer des données aléatoires."""
    
    help = 'Génère des données aléatoires pour PAFFMMO (régions, compétences, héros)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--heroes',
            type=int,
            default=100,
            help='Nombre de héros à créer (défaut: 100)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Effacer toutes les données existantes avant génération'
        )
        parser.add_argument(
            '--clear-heroes',
            action='store_true',
            help='Effacer uniquement les héros existants'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        hero_count = options['heroes']
        
        if hero_count < 1:
            raise CommandError('Le nombre de héros doit être supérieur à 0')
        
        if hero_count > 10000:
            raise CommandError('Le nombre de héros ne peut pas dépasser 10000')

        # Nettoyage des données
        if options['clear']:
            self._clear_all_data()
        elif options['clear_heroes']:
            self._clear_heroes()

        # Création des données de base
        regions = self._create_regions()
        skills = self._create_skills()

        # Création des héros
        created_count = self._create_heroes(hero_count, regions, skills)

        # Résumé
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('Génération terminée avec succès!'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(f'  📍 Régions: {len(regions)}')
        self.stdout.write(f'  ⚔️  Compétences: {len(skills)}')
        self.stdout.write(f'  🦸 Héros créés: {created_count}')
        self.stdout.write(f'  📊 Total héros: {Hero.objects.count()}')

    def _clear_all_data(self):
        """Efface toutes les données."""
        Hero.objects.all().delete()
        Skill.objects.all().delete()
        Region.objects.all().delete()
        self.stdout.write(self.style.WARNING('Toutes les données ont été effacées'))

    def _clear_heroes(self):
        """Efface uniquement les héros."""
        deleted_count = Hero.objects.count()
        Hero.objects.all().delete()
        self.stdout.write(self.style.WARNING(f'{deleted_count} héros effacés'))

    def _create_regions(self) -> List[Region]:
        """Crée ou récupère les régions."""
        regions = []
        for name, env_type in REGION_DATA:
            region, created = Region.objects.get_or_create(
                name=name,
                defaults={'environment_type': env_type}
            )
            regions.append(region)
            if created:
                self.stdout.write(f'  + Région créée: {name}')
        return regions

    def _create_skills(self) -> List[Skill]:
        """Crée ou récupère les compétences."""
        skills = []
        for name, dmg_type, mana in SKILL_DATA:
            skill, created = Skill.objects.get_or_create(
                name=name,
                defaults={'damage_type': dmg_type, 'mana_cost': mana}
            )
            skills.append(skill)
            if created:
                self.stdout.write(f'  + Compétence créée: {name}')
        return skills

    def _create_heroes(
        self, 
        count: int, 
        regions: List[Region], 
        skills: List[Skill]
    ) -> int:
        """Crée les héros aléatoires."""
        region_names = [r.name for r in regions]
        created_count = 0
        attempts = 0
        max_attempts = count * 3  # Limite pour éviter boucle infinie

        self.stdout.write(f'\nCréation de {count} héros...')

        while created_count < count and attempts < max_attempts:
            attempts += 1
            
            # Génération du pseudonyme unique
            nickname = self._generate_nickname()
            if Hero.objects.filter(nickname=nickname).exists():
                continue

            # Génération des statistiques
            job_class = random.choice(JOB_CLASSES)
            level = self._generate_level()
            max_hp = level * 100
            hp_current = random.randint(int(max_hp * 0.3), max_hp)
            xp = level * random.randint(100, 500)
            gold = random.randint(0, level * 100)

            # Génération de la biographie
            biography = self._generate_biography(nickname, region_names)

            # Création du héros
            hero = Hero.objects.create(
                nickname=nickname,
                job_class=job_class,
                level=level,
                hp_current=hp_current,
                xp=xp,
                gold=gold,
                is_active=random.random() > 0.15,  # 85% actifs
                biography=biography,
                region=random.choice(regions) if regions else None,
            )

            # Attribution des compétences
            num_skills = min(random.randint(1, 5), len(skills))
            hero_skills = random.sample(skills, num_skills)
            hero.skills.set(hero_skills)

            created_count += 1
            
            # Affichage de progression
            if created_count % 25 == 0:
                self.stdout.write(f'  ... {created_count}/{count} héros créés')

        return created_count

    def _generate_nickname(self) -> str:
        """Génère un pseudonyme unique."""
        patterns = [
            lambda: f"{fake.first_name()}{random.choice(['_', ''])}{random.randint(1, 999)}",
            lambda: f"{fake.last_name()}{random.choice(['X', 'Z', 'V', ''])}{random.randint(1, 99)}",
            lambda: f"{fake.user_name()}{random.randint(1, 999)}",
            lambda: f"{random.choice(['Dark', 'Shadow', 'Light', 'Fire', 'Ice', 'Storm'])}{fake.first_name()}",
            lambda: f"{fake.first_name()}The{random.choice(['Great', 'Brave', 'Wise', 'Swift'])}",
        ]
        return random.choice(patterns)()

    def _generate_level(self) -> int:
        """Génère un niveau avec distribution réaliste (plus de bas niveaux)."""
        roll = random.random()
        if roll < 0.5:
            return random.randint(1, 20)
        elif roll < 0.8:
            return random.randint(21, 50)
        elif roll < 0.95:
            return random.randint(51, 70)
        else:
            return random.randint(71, 99)

    def _generate_biography(self, nickname: str, region_names: List[str]) -> str:
        """Génère une biographie aléatoire."""
        origin = random.choice(region_names) if region_names else "terres lointaines"
        template = random.choice(BIO_TEMPLATES)
        biography = template.format(nickname=nickname, origin=origin)
        
        # Ajout d'un exploit héroïque
        hook = random.choice(BIO_HOOKS)
        deed = random.choice(BIO_DEEDS)
        biography += f" {hook} {deed}."
        
        return biography
