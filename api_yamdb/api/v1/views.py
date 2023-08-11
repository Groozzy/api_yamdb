from reviews.models import Categories, Genres, Titles
from rest_framework import filters, generics, permissions, viewsets
from .permissions import IsAdminOrReadOnly
from rest_framework.pagination import LimitOffsetPagination

from .serializers import (CategoriesSerializer,
                          GenresSerializer,
                          TitlesSerializer)


class CategoriesViewSet(viewsets.ModelViewSet):
    """Вьюсет для категории."""
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenresViewSet(viewsets.ModelViewSet):
    """Вьюсет для жанра."""
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TitlesViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведения."""
    queryset = Titles.objects.all()
    serializer_class = TitlesSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    filterset_fields = ('category', 'genre', 'name', 'year')
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
