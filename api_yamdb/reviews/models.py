from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

Users = get_user_model()


class Categories(models.Model):
    """Модель категории произведений."""
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name


class Genres(models.Model):
    """Модель жанров произведений."""
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name


class Titles(models.Model):
    """Модель произведений."""
    name = models.CharField(max_length=256)
    year = models.IntegerField()
    genre = models.ManyToManyField(
        Genres,
        through='TitlesGenre')
    category = models.ForeignKey(
        Categories,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles')
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class TitlesGenre(models.Model):
    genres = models.ForeignKey(Genres, on_delete=models.CASCADE)
    titles = models.ForeignKey(Titles, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genres} {self.titles}'


class Reviews(models.Model):
    """Модель отзыва на произведение."""
    title = models.ForeignKey(
        Titles, on_delete=models.CASCADE, related_name='reviews'
    )
    text = models.TextField()
    author = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name='reviews'
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review-title-author'
            )
        ]

    def __str__(self):
        return self.text


class Comments(models.Model):
    """Модель комментария на отзыв."""
    review = models.ForeignKey(
        Reviews, on_delete=models.CASCADE, related_name='comments'
    )
    text = models.TextField()
    author = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name='comments'
    )
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return self.text
