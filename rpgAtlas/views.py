from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render
from django.db import models
from .models import Hero, Region, Skill
from .serializers import HeroSerializer, RegionSerializer, SkillSerializer


class HeroViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hero.objects.select_related('region').prefetch_related('skills').all()
    serializer_class = HeroSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nickname', 'job_class', 'biography']
    ordering_fields = ['level', 'created_at', 'gold']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def by_class(self, request):
        job_class = request.query_params.get('class')
        if job_class:
            heroes = self.queryset.filter(job_class=job_class)
        else:
            heroes = self.queryset
        serializer = self.get_serializer(heroes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = self.queryset.count()
        avg_level = self.queryset.aggregate(avg_level=models.Avg('level'))['avg_level']
        total_gold = self.queryset.aggregate(total_gold=models.Sum('gold'))['total_gold']
        return Response({
            'total_heroes': total,
            'average_level': round(avg_level, 2) if avg_level else 0,
            'total_gold': total_gold or 0,
        })


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.prefetch_related('heroes').all()
    serializer_class = RegionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'environment_type']


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'damage_type']
    ordering_fields = ['mana_cost', 'name']


def index(request):
    return render(request, 'index.html')
