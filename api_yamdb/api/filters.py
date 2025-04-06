from django_filters import FilterSet, CharFilter, NumberFilter

from reviews.models import Title


class TitleFilter(FilterSet):
    """
    Фильтр для модели Title.

    Позволяет фильтровать произведения по названию, категории, жанру и году.
    """
    name = CharFilter(field_name='name', lookup_expr='icontains')
    category = CharFilter(field_name='category__slug', lookup_expr='exact')
    genre = CharFilter(field_name='genre__slug', lookup_expr='exact')
    year = NumberFilter(field_name='year', lookup_expr='exact') 
    # Это поле нет необходимости прописывать явно. 
    # Достаточно добавить его в перечень fields, остальное django-filter сделает сам.

    class Meta:
        model = Title
        fields = ('name', 'category', 'genre', 'year',)
