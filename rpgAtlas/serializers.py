from rest_framework import serializers
from .models import Hero, Region, Skill


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'damage_type', 'mana_cost']


class RegionSerializer(serializers.ModelSerializer):
    hero_count = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = ['id', 'name', 'environment_type', 'hero_count']

    def get_hero_count(self, obj):
        return obj.heroes.count()


class HeroSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', read_only=True, allow_null=True)
    skills = SkillSerializer(many=True, read_only=True)
    job_class_display = serializers.CharField(source='get_job_class_display', read_only=True)

    class Meta:
        model = Hero
        fields = [
            'id', 'nickname', 'job_class', 'job_class_display', 'level',
            'hp_current', 'xp', 'gold', 'is_active', 'biography',
            'created_at', 'region', 'region_name', 'skills',
            'max_hp', 'hp_percentage'
        ]
        read_only_fields = ['created_at']


class HeroListSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', read_only=True, allow_null=True)
    job_class_display = serializers.CharField(source='get_job_class_display', read_only=True)

    class Meta:
        model = Hero
        fields = ['id', 'nickname', 'job_class', 'job_class_display', 'level', 'hp_current', 'xp', 'gold', 'is_active', 'region', 'region_name']
