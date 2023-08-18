from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from rest_framework.decorators import action
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Title, Review
from .filters import TitlesFilter
from .permissions import IsAdminOrReadOnly, IsAuthorOrStaffOrAdminOrReadOnly, IsSuperUser
from .serializers import (CategoriesSerializer,
                          CommentsSerializer,
                          ConfirmationSerializer,
                          CustomUserSerializer,
                          GenresSerializer,
                          ReviewsSerializer,
                          TitlesGetSerializer,
                          TitlesCreateSerializer,
                          SignupSerializer)

User = get_user_model()


class CreateListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Вьюсет, реализующий общий функционал создания, вывод списка, удаления,
    поиска, фильтрации для Категории и Жанров"""
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class CategoriesViewSet(CreateListDestroyViewSet):
    """Вьюсет для категории."""
    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer


class GenresViewSet(CreateListDestroyViewSet):
    """Вьюсет для жанра."""
    queryset = Genre.objects.all()
    serializer_class = GenresSerializer


class TitlesViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведения."""
    queryset = Title.objects.annotate(rating=Avg("reviews__score"))
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('name',)
    filterset_class = TitlesFilter
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitlesGetSerializer
        return TitlesCreateSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    """Вьюсет для публикации."""
    serializer_class = ReviewsSerializer
    permission_classes = (IsAuthorOrStaffOrAdminOrReadOnly,
                          IsAuthenticatedOrReadOnly,)

    def get_title(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title

    def get_queryset(self):
        new_queryset = self.get_title().reviews.select_related('author')
        return new_queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentsViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментариев."""
    serializer_class = CommentsSerializer
    permission_classes = (IsAuthorOrStaffOrAdminOrReadOnly,
                          IsAuthenticatedOrReadOnly)

    def get_review(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review

    def get_queryset(self):
        new_queryset = self.get_review().comments.select_related('author')
        return new_queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class SignupView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request) -> Response:
        serializer = SignupSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        user, _ = User.objects.get_or_create(**serializer.validated_data)
        self.__send_confirmation_code(user.username, user.email)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def __send_confirmation_code(username: str, email: str) -> None:
        user = get_object_or_404(User, username=username)
        confirmation_code: str = default_token_generator.make_token(user)
        send_mail('Confirmation code', confirmation_code, settings.YAMDB_EMAIL,
                  [email])


class ConfirmationView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        confirmation_code = request.data.get('confirmation_code')
        username = request.data.get('username')
        serializer = ConfirmationSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, username=username)
        if default_token_generator.check_token(user, confirmation_code):
            token = AccessToken.for_user(user)
            return Response({'token': str(token)}, status=status.HTTP_200_OK)
        return Response(
            {'confirmation_code': 'confirmation_code is uncorrect'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsSuperUser,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ['patch', 'get', 'post', 'delete']

    @action(methods=['get', 'patch'], detail=False,
            permission_classes=[IsAuthenticated])
    def me(self, request):
        if request.method == 'GET':
            serializer = CustomUserSerializer(self.request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        user = get_object_or_404(User, username=self.request.user)
        serializer = CustomUserSerializer(user, data=request.data,
                                          partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)
