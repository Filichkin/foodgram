from django.core.validators import MinValueValidator
from django.db import models

from foodgram.constants import (
    COOKING_TIME_MIN,
    INGREDIENT_AMOUNT_MIN,
    INGREDIENT_NAME_MAX_LENGTH,
    MEASUREMENT_UNIT_MAX_LENGTH,
    RECIPE_NAME_MAX_LENGTH,
    TAG_NAME_MAX_LENGTH,
    TAG_SLUG_MAX_LENGTH,
)
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        max_length=INGREDIENT_NAME_MAX_LENGTH,
        unique=True,
        verbose_name='Ingredient name',
        help_text='Ingredient name',
    )
    measurement_unit = models.CharField(
        max_length=MEASUREMENT_UNIT_MAX_LENGTH,
        verbose_name='Ingredient measurement unit',
        help_text='Ingredient measurement unit',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient',
            ),
        )

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    name = models.CharField(
        max_length=TAG_NAME_MAX_LENGTH,
        unique=True,
        verbose_name='Tag name',
        help_text='Tag name',
    )
    slug = models.SlugField(
        max_length=TAG_SLUG_MAX_LENGTH,
        unique=True,
        verbose_name='Tag slug',
        help_text='Tag slug',
    )

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=RECIPE_NAME_MAX_LENGTH,
        verbose_name='Recipe name',
        help_text='Recipe name',
    )
    text = models.TextField(
        verbose_name='Recipe description',
        help_text='Recipe description',
    )

    cooking_time = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(
            COOKING_TIME_MIN,
            f'Can not be less than {COOKING_TIME_MIN} minute(s)'
        ),),
        verbose_name='Cooking time in minutes',
        help_text='Cooking time in minutes',
    )
    image = models.ImageField(
        verbose_name='Recipe image',
        help_text='Recipe image',
        upload_to='media/recipes/',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Recipe author',
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTags',
        related_name='recipes',
        verbose_name='Recipe tags',
        help_text='Recipe tags',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_list',
        verbose_name='Recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
        verbose_name='Ingredient'
    )
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(
            INGREDIENT_AMOUNT_MIN,
            f'Minimum amount is {INGREDIENT_AMOUNT_MIN}'
        ),),
        verbose_name='Amount',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Ingredient amount'
        verbose_name_plural = 'Ingredient amounts'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_recipe_ingredient',
            ),
        )

    def __str__(self):
        return f'Recipe {self.recipe} contains ingredient {self.ingredient}'


class RecipeTags(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='tag_list',
        verbose_name='Recipe'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tag_recipe',
        verbose_name='Tag'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Recipe tag'
        verbose_name_plural = 'Recipe tags'
        constraints = [
            models.UniqueConstraint(fields=('recipe', 'tag'),
                                    name='unique_recipe_tag_set')
        ]

    def __str__(self):
        return f'Recipe {self.recipe} has tag {self.tag}'


class UserRecipeBaseModel(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Favorite user',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Favorite recipe',
    )

    class Meta:
        abstract = True
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_unique'
            )
        ]

    def __str__(self):
        return f'{self.recipe} | {self.user}'


class Favorite(UserRecipeBaseModel):

    class Meta(UserRecipeBaseModel.Meta):
        ordering = ['-id']
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        default_related_name = 'favorite'


class ShoppingList(UserRecipeBaseModel):

    class Meta(UserRecipeBaseModel.Meta):
        verbose_name = 'Shopping list'
        verbose_name_plural = 'Shopping lists'
        default_related_name = 'shopping_list'
