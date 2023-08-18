from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

Users = get_user_model()


class Category(models.Model):
    """Модель категории произведений."""
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель жанров произведений."""
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель произведений."""
    name = models.CharField(max_length=256)
    year = models.IntegerField()
    genre = models.ManyToManyField(
        Genre,
        through='TitleGenre')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles')
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class TitleGenre(models.Model):
    genres = models.ForeignKey(Genre, on_delete=models.CASCADE)
    titles = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genres} {self.titles}'


class Review(models.Model):
    """Модель отзыва на произведение."""
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='Автор'
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Оценка'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, db_index=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review-title-author'
            )
        ]
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('pub_date',)

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель комментария на отзыв."""
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, db_index=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('pub_date',)

    def __str__(self):
        return self.text
