from django.db import models


class Region(models.Model):
    name = models.CharField(max_length=100, unique=True)
    environment_type = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Région'
        verbose_name_plural = 'Régions'

    def __str__(self):
        return self.name


class Skill(models.Model):
    DAMAGE_TYPE_CHOICES = [
        ('physical', 'Physique'),
        ('magical', 'Magique'),
        ('healing', 'Soin'),
        ('mixed', 'Mixte'),
    ]

    name = models.CharField(max_length=100)
    damage_type = models.CharField(max_length=20, choices=DAMAGE_TYPE_CHOICES)
    mana_cost = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Compétence'
        verbose_name_plural = 'Compétences'

    def __str__(self):
        return self.name


class Hero(models.Model):
    JOB_CLASS_CHOICES = [
        ('warrior', 'Guerrier'),
        ('mage', 'Mage'),
        ('archer', 'Archer'),
        ('rogue', 'Voleur'),
        ('paladin', 'Paladin'),
        ('cleric', 'Clerc'),
        ('necromancer', 'Nécromancien'),
        ('barbarian', 'Barbare'),
    ]

    nickname = models.CharField(max_length=100, unique=True)
    job_class = models.CharField(max_length=20, choices=JOB_CLASS_CHOICES)
    level = models.IntegerField(default=1)
    hp_current = models.IntegerField(default=100)
    xp = models.IntegerField(default=0)
    gold = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    biography = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='heroes'
    )
    skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name='heroes'
    )

    class Meta:
        verbose_name = 'Héros'
        verbose_name_plural = 'Héros'
        ordering = ['-created_at']

    def __str__(self):
        return self.nickname

    @property
    def max_hp(self):
        return self.level * 100

    @property
    def hp_percentage(self):
        return (self.hp_current / self.max_hp) * 100
