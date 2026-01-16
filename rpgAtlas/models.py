"""
PAFFMMO - Modèles de données
============================
Compatibilité Django 6.0
"""
from django.db import models


class Region(models.Model):
    """Représente une région du monde PAFFMMO."""
    
    name = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name='Nom'
    )
    environment_type = models.CharField(
        max_length=50,
        verbose_name='Type d\'environnement'
    )

    class Meta:
        verbose_name = 'Région'
        verbose_name_plural = 'Régions'
        ordering = ['name']

    def __str__(self):
        return self.name
    
    @property
    def hero_count(self):
        """Retourne le nombre de héros dans cette région."""
        return self.heroes.count()


class Skill(models.Model):
    """Représente une compétence utilisable par les héros."""
    
    class DamageType(models.TextChoices):
        PHYSICAL = 'physical', 'Physique'
        MAGICAL = 'magical', 'Magique'
        HEALING = 'healing', 'Soin'
        MIXED = 'mixed', 'Mixte'

    name = models.CharField(
        max_length=100,
        verbose_name='Nom'
    )
    damage_type = models.CharField(
        max_length=20, 
        choices=DamageType.choices,
        default=DamageType.PHYSICAL,
        verbose_name='Type de dégâts'
    )
    mana_cost = models.PositiveIntegerField(
        default=0,
        verbose_name='Coût en mana'
    )

    class Meta:
        verbose_name = 'Compétence'
        verbose_name_plural = 'Compétences'
        ordering = ['name']

    def __str__(self):
        return self.name


class Hero(models.Model):
    """Représente un héros jouable dans PAFFMMO."""
    
    class JobClass(models.TextChoices):
        WARRIOR = 'warrior', 'Guerrier'
        MAGE = 'mage', 'Mage'
        ARCHER = 'archer', 'Archer'
        ROGUE = 'rogue', 'Voleur'
        PALADIN = 'paladin', 'Paladin'
        CLERIC = 'cleric', 'Clerc'
        NECROMANCER = 'necromancer', 'Nécromancien'
        BARBARIAN = 'barbarian', 'Barbare'

    nickname = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name='Surnom'
    )
    job_class = models.CharField(
        max_length=20, 
        choices=JobClass.choices,
        default=JobClass.WARRIOR,
        verbose_name='Classe'
    )
    level = models.PositiveIntegerField(
        default=1,
        verbose_name='Niveau'
    )
    hp_current = models.PositiveIntegerField(
        default=100,
        verbose_name='HP actuels'
    )
    xp = models.PositiveIntegerField(
        default=0,
        verbose_name='Expérience'
    )
    gold = models.PositiveIntegerField(
        default=0,
        verbose_name='Or'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Actif'
    )
    biography = models.TextField(
        blank=True, 
        default='',
        verbose_name='Biographie'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Créé le'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Modifié le'
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='heroes',
        verbose_name='Région'
    )
    skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name='heroes',
        verbose_name='Compétences'
    )

    class Meta:
        verbose_name = 'Héros'
        verbose_name_plural = 'Héros'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['nickname']),
            models.Index(fields=['job_class']),
            models.Index(fields=['level']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.nickname

    @property
    def max_hp(self):
        """Calcule les HP maximum basés sur le niveau."""
        return self.level * 100

    @property
    def hp_percentage(self):
        """Retourne le pourcentage de HP restants."""
        max_hp = self.max_hp
        if max_hp == 0:
            return 0
        return round((self.hp_current / max_hp) * 100, 1)
    
    def heal(self, amount: int) -> int:
        """Soigne le héros du montant spécifié, sans dépasser max_hp."""
        old_hp = self.hp_current
        self.hp_current = min(self.hp_current + amount, self.max_hp)
        return self.hp_current - old_hp
    
    def take_damage(self, amount: int) -> int:
        """Inflige des dégâts au héros, sans descendre sous 0."""
        old_hp = self.hp_current
        self.hp_current = max(self.hp_current - amount, 0)
        return old_hp - self.hp_current
