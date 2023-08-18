import datetime as dt

from django.contrib.auth import get_user_model
from django.db.models import Avg
from rest_framework import serializers


from reviews.models import (Category, Genre, Title,
                            Review, Comment)

User = get_user_model()


class CategoriesSerializer(serializers.ModelSerializer):
    """Сериализатор для категории произведения."""
    class Meta:
        exclude = ('id',)
        model = Category
        lookup_field = 'slug'


class GenresSerializer(serializers.ModelSerializer):
    """Сериализатор для жанра произведения."""
    class Meta:
        exclude = ('id',)
        model = Genre
        lookup_field = 'slug'


class TitlesSerializer(serializers.ModelSerializer):
    """Сериализатор для произведения."""
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug')
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Title

    def to_representation(self, instance):
        self.fields['category'] = CategoriesSerializer()
        self.fields['genre'] = GenresSerializer(many=True)
        return super().to_representation(instance)

    def validate_year(self, value):
        """Валидация года создания."""
        current_year = dt.date.today().year
        if value > current_year:
            raise serializers.ValidationError(
                'Год создания не может быть в будущем')
        return value

    @staticmethod
    def get_rating(obj):
        avg_rating = (
            Title.objects.filter(id=obj.id)
            .annotate(average_rating=Avg("reviews__score"))
            .values("average_rating")
            .first()
        )
        if avg_rating['average_rating'] is None:
            return None
        return round(avg_rating['average_rating'], 1)


class ReviewsSerializer(serializers.ModelSerializer):
    """Сериализатор для отзыва к произведению."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        title = self.context.get('view').kwargs.get('title_id')
        request = self.context.get('request')
        if (request.method == "POST"
            and Review.objects.filter(
                author=request.user, title=title).exists()):
            raise serializers.ValidationError('Validation fault.')
        return data

    def validate_score(self, value):
        """Валидация оценки."""
        if not (1 <= value <= 10):
            raise serializers.ValidationError('Оценка может быть от 1 до 10')
        return value


class CommentsSerializer(serializers.ModelSerializer):
    """Сериализатор для комментрия к отзыву."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class SignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email')

    @staticmethod
    def validate(data):
        if data['username'] == 'me':
            raise serializers.ValidationError('Нельзя использовать имя "me"')
        return data


class ConfirmationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email', 'role', 'bio')
        lookup_field = 'username'
