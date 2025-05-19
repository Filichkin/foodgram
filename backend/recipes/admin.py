from django import forms
from django.contrib import admin

from foodgram.constants import INLINE_EXTRA
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag


class RecipeIngredientsInLine(admin.TabularInline):
    model = RecipeIngredient
    extra = INLINE_EXTRA


class RecipeTagsInLine(admin.TabularInline):
    model = Recipe.tags.through
    extra = INLINE_EXTRA


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    empty_value_display = '-empty-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name',)
    empty_value_display = '-empty-'


class RecipeAdminForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        ingredients = cleaned_data.get('ingredients')
        tags = cleaned_data.get('tags')
        if not ingredients or ingredients.count() == 0:
            raise forms.ValidationError(
                'Please add ingredients')
        if not tags or tags.count() == 0:
            raise forms.ValidationError(
                'Please add tags')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'text', 'author', 'favorite_count')
    search_fields = ('name', 'author')
    list_filter = ('tags',)
    inlines = (RecipeIngredientsInLine, RecipeTagsInLine)
    empty_value_display = '-empty-'

    def favorite_count(self, recipe: Recipe):
        return recipe.favorite.count()

    favorite_count.short_description = 'Count of favorites recipes'
