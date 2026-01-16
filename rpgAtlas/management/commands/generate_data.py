import random
from faker import Faker
from django.core.management.base import BaseCommand
from rpgAtlas.models import Hero, Region, Skill

fake = Faker(['fr_FR'])

JOB_CLASSES = ['warrior', 'mage', 'archer', 'rogue', 'paladin', 'cleric', 'necromancer', 'barbarian']

REGION_NAMES = [
    ('Royaume d\'Eldoria', 'forest'),
    ('Montagnes de Fer', 'mountain'),
    ('Côtes des Tempêtes', 'coastal'),
    ('Désert de Sable Rouge', 'desert'),
    ('Terres Gelées du Nord', 'snowy'),
    ('Vallée des Ombres', 'swamp'),
    ('Plaines de l\'Aube', 'plains'),
    ('Forêt Mystique', 'forest'),
    ('Volcan de Feu Noir', 'volcanic'),
    ('Iles Perdues', 'island'),
]

SKILL_DATA = [
    ('Coup Puissant', 'physical', 10),
    ('Boule de Feu', 'magical', 25),
    ('Tir Précis', 'physical', 15),
    ('Assassinat', 'physical', 30),
    ('Bouclier Sacré', 'healing', 20),
    ('Soin', 'healing', 15),
    ('Malédiction', 'magical', 35),
    ('Rugissement', 'physical', 20),
    ('Foudre', 'magical', 30),
    ('Poison', 'mixed', 25),
    ('Glace', 'magical', 28),
    ('Prière', 'healing', 10),
    ('Faim du Loup', 'physical', 22),
    ('Tentacules', 'magical', 40),
    ('Masse Divin', 'physical', 45),
]

BIO_TEMPLATES = [
    "Originaire de {origin}, {nickname} a quitté son village natal après une tragédie qui a décimé sa famille. Depuis, il parcours le monde en quête de vengeance et de gloire.",
    "{nickname} est un héros légendaire dont les exploits sont chantés dans toutes les tavernes du royaume. On dit qu'il a vaincu le dragon noir à lui seul.",
    "Élevé par des moines guerriers, {nickname} a appris l'art de la combat dès son plus jeune âge. Sa sagesse et sa force en font un allié précieux.",
    "Ancien mercenaire, {nickname} a laissé derrière lui un passé trouble. Aujourd'hui, il cherche la rédemption en aidant les plus faibles.",
    "{nickname} est né sous une lune rouge, ce qui lui confère des pouvoirs étranges. Les villageois le craignent, mais les monstres le redoutent encore plus.",
    "Chevalier sans maître, {nickname} erre à travers le royaume en quête d'honneur et de défis. Sa lame ne connaît pas la défaite.",
    "Magicien exilé de sa tour pour expériences interdites, {nickname} parcourt les terres sauvages en quête de connaissances perdues.",
    "{nickname} était autrefois un garde royal avant de découvrir la corruption au sein de la cour. Il a fui pour échapper au bûcher.",
    "Né dans les mines profondes, {nickname} a forgé sa propre destinée à coups de marteau et d'épée. Sa réputation le précède.",
    "{nickname} est un chasseur de primes intrépide. Sa cible actuelle : le seigneur noir qui terrorise la région.",
    "Orphelin élevé dans les rues, {nickname} a appris à survivre par la ruse et la vitesse. Personne ne l'attrape.",
    "Descendant d'une lignée de rois tombés, {nickname} porte le fardeau de restaurer la gloire de ses ancêtres.",
    "{nickname} a fait vœu de silence il y a des années. Seuls ses actes parlent pour lui, et ses actes sont éloquents.",
    "Guérisseur mystérieux, {nickname} apparaît là où le besoin se fait sentir. On murmure qu'il peut ranimer les morts.",
    "{nickname} est un samouraï perdu dans ce monde étrange. Son code de l'honneur est inflexible, sa lame imparable.",
]

BIO_HOOKS = [
    "On raconte qu'il a",
    "Sa réputation repose sur",
    "Les chroniques mentionnent",
    "Les bardes chantent",
    "Les rumeurs suggèrent",
    "Les survivants témoignent",
    "Les archives royales révèlent",
    "Les старых легенды (anciennes légendes) parlent",
]

BIO_DEEDS = [
    "vaincu un démon ancestral dans les profondeurs",
    "protégé le village pendant trois semaines sans repos",
    "trouvé le trésor perdu du roi maudit",
    "guéri la plague noire qui ravageait les campagnes",
    "défié l'empereur en combat singulier",
    "sauvé la princesse des griffes du dragon",
    "découvert un passage secret vers les souterrains",
    "apprivoisé une créature sauvage pour monture",
    "résolu l'énigme de la tour hantée",
    "rejeté l'offre du diable lui-même",
]

REGION_NAMES_LIST = [r[0] for r in REGION_NAMES]

SKILL_DATA = [
    ('Coup Puissant', 'physical', 10),
    ('Boule de Feu', 'magical', 25),
    ('Tir Précis', 'physical', 15),
    ('Assassinat', 'physical', 30),
    ('Bouclier Sacré', 'healing', 20),
    ('Soin', 'healing', 15),
    ('Malédiction', 'magical', 35),
    ('Rugissement', 'physical', 20),
    ('Foudre', 'magical', 30),
    ('Poison', 'mixed', 25),
    ('Glace', 'magical', 28),
    ('Prière', 'healing', 10),
    ('Faim du Loup', 'physical', 22),
    ('Tentacules', 'magical', 40),
    ('Masse Divin', 'physical', 45),
]


class Command(BaseCommand):
    help = 'Génère des données aléatoires pour PAFFMMO'

    def add_arguments(self, parser):
        parser.add_argument('--heroes', type=int, default=100, help='Nombre de héros à créer')
        parser.add_argument('--clear', action='store_true', help='Effacer les données existantes')

    def handle(self, *args, **options):
        if options['clear']:
            Hero.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Données existantes effacées'))

        regions = []
        for name, env_type in REGION_NAMES:
            region, created = Region.objects.get_or_create(name=name, defaults={'environment_type': env_type})
            regions.append(region)

        skills = []
        for name, dmg_type, mana in SKILL_DATA:
            skill, created = Skill.objects.get_or_create(name=name, defaults={'damage_type': dmg_type, 'mana_cost': mana})
            skills.append(skill)

        hero_count = 0
        for _ in range(options['heroes']):
            nickname = fake.user_name() + str(random.randint(1, 999))
            if Hero.objects.filter(nickname=nickname).exists():
                continue

            job_class = random.choice(JOB_CLASSES)
            level = random.randint(1, 80)
            max_hp = level * 100
            hp_current = random.randint(1, max_hp)
            xp = level * random.randint(100, 500)
            gold = random.randint(0, 5000)

            origin = random.choice(REGION_NAMES_LIST)
            deed = random.choice(BIO_DEEDS)

            biography_template = random.choice(BIO_TEMPLATES)
            biography = biography_template.format(nickname=nickname, origin=origin)
            biography += f" {random.choice(BIO_HOOKS)} {deed}."

            hero = Hero.objects.create(
                nickname=nickname,
                job_class=job_class,
                level=level,
                hp_current=hp_current,
                xp=xp,
                gold=gold,
                is_active=random.choice([True, True, True, False]),
                biography=biography,
                region=random.choice(regions) if regions else None,
            )

            num_skills = random.randint(1, 5)
            hero_skills = random.sample(skills, num_skills)
            hero.skills.set(hero_skills)

            hero_count += 1

        self.stdout.write(self.style.SUCCESS(f'{hero_count} héros créés avec succès!'))
        self.stdout.write(f'Régions: {len(regions)}')
        self.stdout.write(f'Compétences: {len(skills)}')
