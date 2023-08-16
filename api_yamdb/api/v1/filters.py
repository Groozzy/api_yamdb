from django_filters import FilterSet, AllValuesFilter
from reviews.models import Title


class TitlesFilter(FilterSet):
    """Фильтрация для модели Titles"""

    category = AllValuesFilter(field_name='category__slug')
    genre = AllValuesFilter(field_name='genre__slug')

    class Meta:
        model = Title
        fields = ['category', 'genre', 'name', 'year']
