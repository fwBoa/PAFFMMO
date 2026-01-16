from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HeroViewSet, RegionViewSet, SkillViewSet, index

router = DefaultRouter()
router.register(r'heroes', HeroViewSet, basename='hero')
router.register(r'regions', RegionViewSet, basename='region')
router.register(r'skills', SkillViewSet, basename='skill')

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', HeroViewSet.as_view({'get': 'stats'}), name='hero-stats'),
    path('index/', index, name='index'),
]
