from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from reviews.models import Categories, Genres, Reviews, Titles
from .filters import TitlesFilter
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (CategoriesSerializer, CommentsSerializer,
                          GenresSerializer, ReviewsSerializer,
                          SignupSerializer, TitlesSerializer)

User = get_user_model()


class SpecialViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """ Специальный вьюсет для Категории и Жанров"""
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class CategoriesViewSet(SpecialViewSet):
    """Вьюсет для категории."""
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer


class GenresViewSet(SpecialViewSet):
    """Вьюсет для жанра."""
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer


class TitlesViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведения."""
    queryset = Titles.objects.all()
    serializer_class = TitlesSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('name',)
    filterset_class = TitlesFilter
    permission_classes = (IsAdminOrReadOnly,)


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


class SignupView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request) -> Response:
        username = request.data.get('username')
        email = request.data.get('email')

        if User.objects.filter(username=username).exists():
            if User.objects.get(username=username).email != email:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            self.__send_confirmation_code(username, email)
            return Response(status=status.HTTP_200_OK)

        serializer = SignupSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.__send_confirmation_code(username, email)
        return Response(serializer.data)

    @staticmethod
    def __send_confirmation_code(username: str, email: str) -> None:
        user = get_object_or_404(User, username=username)
        confirmation_code: str = default_token_generator.make_token(user)
        send_mail('Confirmation code', confirmation_code, settings.ADMIN_EMAIL,
                  [email])
