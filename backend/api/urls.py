from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    UserViewSet,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet
)


app_name = 'api'

router = DefaultRouter()

router.register('users', UserViewSet, 'users')
router.register('ingredients', IngredientViewSet, 'ingredients')
router.register('recipes', RecipeViewSet, 'recipes')
router.register('tags', TagViewSet, 'tags')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
