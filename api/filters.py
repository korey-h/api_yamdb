from django_filters import filters
from django_filters.rest_framework.filterset import FilterSet

from .models import Titles


class TitleFilter(FilterSet):
    genre = filters.CharFilter(field_name='genre__slug',
                               lookup_expr='exact')
    category = filters.CharFilter(field_name='category__slug',
                                  lookup_expr='exact')
    name = filters.CharFilter(field_name='name',
                              lookup_expr='contains')

    class Meta:
        model = Titles
        fields = ['year', ]
