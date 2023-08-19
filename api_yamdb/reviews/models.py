from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

Users = get_user_model()


class Category(models.Model):
    """Модель категории произведений."""
    name = models.CharField(max_length=256,
                            verbose_name="Название категории")
    slug = models.SlugField(unique=True, max_length=50,
                            verbose_name="Слаг категории")

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель жанров произведений."""
    name = models.CharField(max_length=256, verbose_name="Название жанра")
    slug = models.SlugField(unique=True, max_length=50,
                            verbose_name="Слаг жанра")

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель произведений."""
    name = models.CharField(max_length=256,
                            verbose_name="Название произведения")
    year = models.PositiveSmallIntegerField(
        verbose_name="Год создания произведения")
    genre = models.ManyToManyField(
        Genre,
        through='TitleGenre',
        verbose_name="Жанр произведения")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name="Категория произведения")
    description = models.TextField(null=True, blank=True,
                                   verbose_name="Описание произведения")

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

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
        verbose_name="Название произведения"
    )
    text = models.TextField(verbose_name="Текст отзыва")
    author = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name='reviews',
        verbose_name="Автор отзыва"
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Оценка"
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
        verbose_name = 'Отзыв на произведение'
        verbose_name_plural = 'Отзывы на произведения'
        ordering = ('pub_date',)

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель комментария на отзыв."""
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments',
        verbose_name="Отзыв"

    )
    text = models.TextField(verbose_name="Текст комментария")
    author = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name='comments',
        verbose_name="Автор"
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, db_index=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('pub_date',)

    def __str__(self):
        return self.text
