from django_filters import rest_framework as django_filter
from django.db.models.query import QuerySet

from recipes.models import Recipe

BOOLEAN_ENUM = ((0, 'false'), (1, 'true'))


class RecipeFilter(django_filter.FilterSet):

    is_favorited = django_filter.ChoiceFilter(
        choices=BOOLEAN_ENUM,
        method='filter_favorited'
    )
    is_in_shopping_cart = django_filter.ChoiceFilter(
        choices=BOOLEAN_ENUM,
        method='filter_shopping'
    )
    tags = django_filter.CharFilter(
        field_name='tags__slug'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def filter_favorited(self, queryset: QuerySet, name: str,
                         value: bool) -> QuerySet:
        return queryset.filter(is_favorited=value)

    def filter_shopping(self, queryset: QuerySet, name: str,
                        value: bool) -> QuerySet:
        return queryset.filter(is_in_shopping_cart=value)
