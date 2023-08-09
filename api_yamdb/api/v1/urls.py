from django.urls import include, path
from .views import (CategoriesViewSet, GenresViewSet, TitlesViewSet)
from rest_framework.routers import SimpleRouter


router = SimpleRouter()
router.register('categories', CategoriesViewSet)
router.register('genres', GenresViewSet)
router.register('titles', TitlesViewSet)


urlpatterns = [
    path('', include(router.urls)),
]