import datetime as dt

from django.contrib.auth import get_user_model
from django.db.models import Avg
from rest_framework import serializers


from reviews.models import (Categories, Genres, Titles,
                            Reviews, Comments)

User = get_user_model()


class CategoriesSerializer(serializers.ModelSerializer):
    """Сериализатор для категории произведения."""
    class Meta:
        exclude = ('id',)
        model = Categories
        lookup_field = 'slug'


class GenresSerializer(serializers.ModelSerializer):
    """Сериализатор для жанра произведения."""
    class Meta:
        exclude = ('id',)
        model = Genres
        lookup_field = 'slug'


class TitlesSerializer(serializers.ModelSerializer):
    """Сериализатор для произведения."""
    category = serializers.SlugRelatedField(
        queryset=Categories.objects.all(),
        slug_field='slug')
    genre = serializers.SlugRelatedField(
        queryset=Genres.objects.all(),
        slug_field='slug',
        many=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Titles

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
  
    def get_rating(self, obj):
        avg_rating = (
            Titles.objects.filter(id=obj.id)
            .annotate(average_rating=Avg("reviews__score"))
            .values("average_rating")
            .first()
        )
        if avg_rating['average_rating'] is None:
            return 'None'
        return round(avg_rating['average_rating'], 1)


class ReviewsSerializer(serializers.ModelSerializer):
    """Сериализатор для отзыва к произведению."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Reviews

    def validate(self, data):
        title = self.context.get('view').kwargs.get('title_id')
        request = self.context.get('request')
        if (request.method == "POST"
            and Reviews.objects.filter(
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
        model = Comments


class SignupSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email')
