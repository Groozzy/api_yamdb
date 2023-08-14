from django.shortcuts import get_object_or_404
from reviews.models import Categories, Genres, Titles, Reviews
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (CategoriesSerializer,
                          CommentsSerializer,
                          GenresSerializer,
                          ReviewsSerializer,
                          TitlesSerializer)


class CategoriesViewSet(viewsets.ModelViewSet):
    """Вьюсет для категории."""
    queryset = Categories.objects.all()
    lookup_field = 'slug'
    serializer_class = CategoriesSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenresViewSet(viewsets.ModelViewSet):
    """Вьюсет для жанра."""
    queryset = Genres.objects.all()
    lookup_field = 'slug'
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
    filterset_fields = ('category__slug', 'genre__slug', 'name', 'year')
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = LimitOffsetPaginationlizer, ReviewsSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    """Вьюсет для публикации."""
    serializer_class = ReviewsSerializer
    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly)

    def get_title(self):
        title = get_object_or_404(Titles, pk=self.kwargs.get('title_id'))
        return title

    def get_queryset(self):
        new_queryset = self.get_title().reviews.select_related('author')
        return new_queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentsViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментариев."""
    serializer_class = CommentsSerializer
    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly)

    def get_review(self):
        review = get_object_or_404(Reviews, pk=self.kwargs.get('review_id'))
        return review

    def get_queryset(self):
        new_queryset = self.get_review().comments.select_related('author')
        return new_queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
