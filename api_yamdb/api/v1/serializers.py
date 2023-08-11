from rest_framework import serializers

from reviews.models import Categories, Genres, Titles, TitlesGenre

import datetime as dt


class CategoriesSerializer(serializers.ModelSerializer):
    """Сериализатор для категории произведения."""
    class Meta:
        fields = '__all__'
        model = Categories


class GenresSerializer(serializers.ModelSerializer):
    """Сериализатор для жанра произведения."""
    class Meta:
        fields = '__all__'
        model = Genres


class TitlesSerializer(serializers.ModelSerializer):
    """Сериализатор для произведения."""
    genre = GenresSerializer(many=True, read_only=True)

    class Meta:
        fields = '__all__'
        model = Titles
    
    # def create(self, validated_data):
    #     """Создание произведения со списком жанров."""
    #     # Уберём список жанров из словаря validated_data и сохраним его
    #     genre = validated_data.pop('genre')
    #     # Сначала добавляем произведением в БД
    #     title = Titles.objects.create(**validated_data)
    #     # А потом добавляем его жанры в БД
    #     for i in genre:
    #         current_i, status = Genres.objects.get_or_create(
    #             **i)
    #         # связываем каждый жанр с произведением
    #         TitlesGenre.objects.create(
    #             genre=current_i, title=title)
    #     return title

    def validate_year(self, value):
        """Валидация года создания."""
        current_year = dt.date.today().year
        if value > current_year:
            raise serializers.ValidationError(
                'Год создания не может быть в будущем')
        return value
