"""
PAFFMMO - Serializers
=====================
Compatibilité DRF 3.15+
"""
from rest_framework import serializers
from .models import Hero, Region, Skill


class SkillSerializer(serializers.ModelSerializer):
    """Serializer pour les compétences."""
    
    damage_type_display = serializers.CharField(
        source='get_damage_type_display', 
        read_only=True
    )
    heroes_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Skill
        fields = [
            'id', 
            'name', 
            'damage_type', 
            'damage_type_display',
            'mana_cost',
            'heroes_count',
        ]


class RegionSerializer(serializers.ModelSerializer):
    """Serializer pour les régions."""
    
    heroes_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Region
        fields = [
            'id', 
            'name', 
            'environment_type', 
            'heroes_count',
        ]


class HeroListSerializer(serializers.ModelSerializer):
    """Serializer léger pour la liste des héros."""
    
    region_name = serializers.CharField(
        source='region.name', 
        read_only=True, 
        allow_null=True,
        default=None
    )
    job_class_display = serializers.CharField(
        source='get_job_class_display', 
        read_only=True
    )
    max_hp = serializers.IntegerField(read_only=True)
    hp_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = Hero
        fields = [
            'id', 
            'nickname', 
            'job_class', 
            'job_class_display', 
            'level', 
            'hp_current',
            'max_hp',
            'hp_percentage',
            'xp', 
            'gold', 
            'is_active', 
            'region', 
            'region_name',
            'created_at',
        ]


class HeroSerializer(serializers.ModelSerializer):
    """Serializer complet pour le détail d'un héros."""
    
    region_name = serializers.CharField(
        source='region.name', 
        read_only=True, 
        allow_null=True,
        default=None
    )
    region_data = RegionSerializer(source='region', read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    job_class_display = serializers.CharField(
        source='get_job_class_display', 
        read_only=True
    )
    max_hp = serializers.IntegerField(read_only=True)
    hp_percentage = serializers.FloatField(read_only=True)
    skills_count = serializers.SerializerMethodField()

    class Meta:
        model = Hero
        fields = [
            'id', 
            'nickname', 
            'job_class', 
            'job_class_display', 
            'level',
            'hp_current', 
            'max_hp',
            'hp_percentage',
            'xp', 
            'gold', 
            'is_active', 
            'biography',
            'created_at', 
            'updated_at',
            'region', 
            'region_name',
            'region_data',
            'skills',
            'skills_count',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_skills_count(self, obj):
        """Retourne le nombre de compétences du héros."""
        return obj.skills.count()
