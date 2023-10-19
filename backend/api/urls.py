from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                    TagViewSet, UserViewSet)

app_name = 'api'

router = DefaultRouter()
router.register(
    'tags',
    TagViewSet,
    'tags'
)
router.register(
    'ingredients',
    IngredientViewSet,
    'ingredients'
)
router.register(
    'recipes',
    RecipeViewSet,
    'recipe'
)
router.register(
    'users',
    UserViewSet,
    'users'
)
urlpatterns = (
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('recipes/<id>/favorite/',
         FavoriteViewSet.as_view(
             {'post': 'favorite', 'delete': 'favorite'}),
         name='favorite'
         ),
)
