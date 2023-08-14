import datetime as dt

from rest_framework import serializers

from reviews.models import (Categories, Genres, Titles,
                            TitlesGenre, Reviews, Comments)




class CategoriesSerializer(serializers.ModelSerializer):
    """Сериализатор для категории произведения."""
    class Meta:
        # fields = '__all__'
        exclude = ('id',)
        model = Categories
        lookup_field = 'slug'


class GenresSerializer(serializers.ModelSerializer):
    """Сериализатор для жанра произведения."""
    class Meta:
        # fields = '__all__'
        exclude = ('id',)
        model = Genres
        lookup_field = 'slug'


class TitlesSerializer(serializers.ModelSerializer):
    """Сериализатор для произведения."""
    # категория может быть из БД категорий
    category = serializers.SlugRelatedField(
        queryset=Categories.objects.all(),
        slug_field='slug')
    genre = serializers.SlugRelatedField(
        queryset=Genres.objects.all(),
        slug_field='slug',
        many=True)

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


class ReviewsSerializer(serializers.ModelSerializer):
    """Сериализатор для отзыва к произведению."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Reviews

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
