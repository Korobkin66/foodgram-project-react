from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TagViewSet, IngredientViewSet, RecipeViewSet

app_name = 'api'

router = DefaultRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredient', IngredientViewSet, basename='ingredient')


urlpatterns = [
    path("auth/", include("djoser.urls.authtoken")),
    path('', include('djoser.urls')),
    path('', include(router.urls)),
]
