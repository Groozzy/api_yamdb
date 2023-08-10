from django.db import models


class Categories(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name


class Genres(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name


class Titles(models.Model):
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
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class TitlesGenre(models.Model):
    genres = models.ForeignKey(Genres, on_delete=models.CASCADE)
    titles = models.ForeignKey(Titles, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genres} {self.titles}'
