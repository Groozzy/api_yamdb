from rest_framework import serializers

from reviews.models import Reviews, Comments


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
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comments
