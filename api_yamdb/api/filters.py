import django_filters

from reviews.models import Title


class MyTitleFilter(django_filters.FilterSet):
    genre = django_filters.CharFilter(field_name='genre__slug',
                                      lookup_expr='contains')
    category = django_filters.CharFilter(field_name='category__slug',
                                         lookup_expr='contains')
    name = django_filters.CharFilter(field_name='name')
    year = django_filters.NumberFilter(field_name='year')

    class Meta:
        model = Title
        fields = ('name', 'year', 'category', 'genre')
