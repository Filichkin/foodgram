import django_filters
from rest_framework import filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(filters.SearchFilter):
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(django_filters.rest_framework.FilterSet):
    tags = django_filters.rest_framework.filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
        label='Tags'
    )
    is_favorited = django_filters.rest_framework.filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = django_filters.rest_framework.filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        user = (
            self.request.user
            if self.request.user.is_authenticated
            else None
        )
        if value and user:
            return queryset.filter(favorite__user_id=user.id)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = (
            self.request.user
            if self.request.user.is_authenticated
            else None
        )
        if value and user:
            return queryset.filter(shopping_list__user_id=user.id)
        return queryset
