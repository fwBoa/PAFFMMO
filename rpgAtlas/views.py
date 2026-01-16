"""
PAFFMMO - API Views
===================
Compatibilité Django 6.0 & DRF 3.15
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render
from django.db.models import Avg, Sum, Count, Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .models import Hero, Region, Skill
from .serializers import HeroSerializer, HeroListSerializer, RegionSerializer, SkillSerializer


class HeroViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les héros.
    
    Endpoints:
    - GET /api/heroes/ : Liste paginée des héros
    - GET /api/heroes/{id}/ : Détail d'un héros
    - GET /api/heroes/by_class/ : Filtrer par classe
    - GET /api/heroes/stats/ : Statistiques globales
    - GET /api/heroes/top/ : Top héros par niveau
    """
    queryset = Hero.objects.select_related('region').prefetch_related('skills')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nickname', 'job_class', 'biography']
    ordering_fields = ['level', 'created_at', 'gold', 'xp', 'hp_current']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Utilise un serializer léger pour la liste."""
        if self.action == 'list':
            return HeroListSerializer
        return HeroSerializer

    def get_queryset(self):
        """Filtre optionnel par classe et statut actif."""
        queryset = super().get_queryset()
        
        job_class = self.request.query_params.get('job_class')
        if job_class:
            queryset = queryset.filter(job_class=job_class)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        region_id = self.request.query_params.get('region')
        if region_id:
            queryset = queryset.filter(region_id=region_id)
        
        min_level = self.request.query_params.get('min_level')
        if min_level:
            queryset = queryset.filter(level__gte=int(min_level))
        
        max_level = self.request.query_params.get('max_level')
        if max_level:
            queryset = queryset.filter(level__lte=int(max_level))
        
        return queryset

    @action(detail=False, methods=['get'])
    def by_class(self, request):
        """Retourne les héros filtrés par classe."""
        job_class = request.query_params.get('class')
        if not job_class:
            return Response(
                {'error': 'Le paramètre "class" est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        heroes = self.get_queryset().filter(job_class=job_class)
        page = self.paginate_queryset(heroes)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(heroes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60))  # Cache 1 minute
    def stats(self, request):
        """Retourne les statistiques globales des héros."""
        queryset = self.get_queryset()
        
        stats = queryset.aggregate(
            total_heroes=Count('id'),
            avg_level=Avg('level'),
            total_gold=Sum('gold'),
            total_xp=Sum('xp'),
            avg_gold=Avg('gold'),
        )
        
        # Répartition par classe
        class_distribution = (
            queryset
            .values('job_class')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Répartition par région
        region_distribution = (
            queryset
            .exclude(region__isnull=True)
            .values('region__name')
            .annotate(count=Count('id'), avg_level=Avg('level'))
            .order_by('-count')
        )
        
        return Response({
            'total_heroes': stats['total_heroes'] or 0,
            'average_level': round(stats['avg_level'] or 0, 2),
            'total_gold': stats['total_gold'] or 0,
            'total_xp': stats['total_xp'] or 0,
            'average_gold': round(stats['avg_gold'] or 0, 2),
            'class_distribution': list(class_distribution),
            'region_distribution': list(region_distribution),
        })

    @action(detail=False, methods=['get'])
    def top(self, request):
        """Retourne le top des héros par niveau."""
        limit = int(request.query_params.get('limit', 10))
        limit = min(limit, 100)  # Max 100
        
        heroes = self.get_queryset().order_by('-level', '-xp')[:limit]
        serializer = self.get_serializer(heroes, many=True)
        return Response(serializer.data)


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les régions."""
    queryset = Region.objects.prefetch_related('heroes').annotate(
        heroes_count=Count('heroes')
    )
    serializer_class = RegionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'environment_type']
    ordering_fields = ['name', 'heroes_count']
    ordering = ['name']


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les compétences."""
    queryset = Skill.objects.prefetch_related('heroes').annotate(
        heroes_count=Count('heroes')
    )
    serializer_class = SkillSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'damage_type']
    ordering_fields = ['mana_cost', 'name', 'heroes_count']
    ordering = ['name']

    def get_queryset(self):
        """Filtre optionnel par type de dégâts."""
        queryset = super().get_queryset()
        
        damage_type = self.request.query_params.get('damage_type')
        if damage_type:
            queryset = queryset.filter(damage_type=damage_type)
        
        return queryset


def index(request):
    """Vue principale - Atlas interactif."""
    return render(request, 'index.html')
