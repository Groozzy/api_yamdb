from reviews.models import Categories, Genres, Titles
from rest_framework import filters, generics, permissions, viewsets
#from rest_framework.pagination import LimitOffsetPagination

from .serializers import (CategoriesSerializer, GenresSerializer,
                          TitlesSerializer)


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    # permission_classes = (permissions.IsAdminUser,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenresViewSet(viewsets.ModelViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    permission_classes = (permissions.IsAdminUser,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Titles.objects.all()
    serializer_class = TitlesSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    filterset_fields = ('category', 'genre', 'name', 'year')
    permission_classes = (permissions.IsAdminUser,)
    # pagination_class = LimitOffsetPagination
