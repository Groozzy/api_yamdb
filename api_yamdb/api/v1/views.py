from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Categories, Genres, Titles, Reviews
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly, IsSuperUser
from .serializers import (CategoriesSerializer,
                          CommentsSerializer,
                          ConfirmationSerializer,
                          CustomUserSerializer,
                          GenresSerializer,
                          ReviewsSerializer,
                          TitlesSerializer,
                          SignupSerializer)

User = get_user_model()


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
    pagination_class = LimitOffsetPagination


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
