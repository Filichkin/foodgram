from django.contrib import admin

from foodgram.constants import INLINE_EXTRA, MIN_NUM
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag


class RecipeIngredientsInLine(admin.TabularInline):
    model = RecipeIngredient
    extra = INLINE_EXTRA
    min_num = MIN_NUM


class RecipeTagsInLine(admin.TabularInline):
    model = Recipe.tags.through
    extra = INLINE_EXTRA
    min_num = MIN_NUM


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
