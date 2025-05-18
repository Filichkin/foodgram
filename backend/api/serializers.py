from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from foodgram.constants import PAGE_SIZE
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTags,
    ShoppingList,
    Tag
)
from users.models import Follow, User


class UserSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.subscriptions.filter(author=obj).exists()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = ('avatar',)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):

    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = RecipeIngredientSerializer(
        source='ingredient_list',
        many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def check_user_status(self, obj, model_class):
        user = self.context.get('request')
        return bool(
            user
            and user.user.is_authenticated
            and model_class.objects.filter(
                recipe=obj,
                user=user.user
            ).exists()
        )

    def get_is_favorited(self, obj):
        return self.check_user_status(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.check_user_status(obj, ShoppingList)


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        label='Tags',
    )
    ingredients = RecipeIngredientWriteSerializer(
        many=True,
        label='Ingredients',
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(
                'Please add tag')

        if len(value) != len(set(value)):
            raise serializers.ValidationError('Tags must be unique')

        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'Please add ingredient'
            )
        ingredient_ids = [ingredient['id'] for ingredient in value]
        existing_ingredients = Ingredient.objects.filter(id__in=ingredient_ids)
        if len(existing_ingredients) != len(ingredient_ids):
            missing_ids = set(ingredient_ids) - set(
                existing_ingredients.values_list('id', flat=True)
            )
            raise serializers.ValidationError(
                f'Ingredients with id {missing_ids} do not exist'
            )
        return value

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(
            instance, context={'request': self.context.get('request')}
        )
        return serializer.data

    def create_tags(self, tags, recipe):
        recipe.tags.set(tags)

    def create_ingredients(self, ingredients, recipe):
        for ingredient_data in ingredients:
            ingredient_id = ingredient_data['id']
            ingredient = Ingredient.objects.get(pk=ingredient_id)
            amount = ingredient_data['amount']
            RecipeIngredient.objects.create(
                ingredient=ingredient,
                recipe=recipe,
                amount=amount
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        user = self.context.get('request').user
        recipe = Recipe.objects.create(**validated_data, author=user)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.get('tags')
        if tags is None:
            raise serializers.ValidationError(
                {'tags': 'Please add tag'}
            )
        ingredients = validated_data.get('ingredients')
        if ingredients is None:
            raise serializers.ValidationError(
                {'ingredients': 'Please add ingredient'}
            )
        RecipeTags.objects.filter(recipe=instance).delete()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_tags(validated_data.pop('tags'), instance)
        self.create_ingredients(validated_data.pop('ingredients'), instance)
        return super().update(instance, validated_data)


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriberDetailSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = Base64ImageField(source='author.avatar')

    class Meta:
        model = Follow
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return Follow.objects.filter(author=obj.author, user=user).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit', PAGE_SIZE)
        try:
            limit = int(limit)
        except ValueError:
            pass
        return ShortRecipeSerializer(
            Recipe.objects.filter(author=obj.author)[:limit],
            many=True,
            context={'request': request},
        ).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class SubscriberSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = '__all__'
        read_only_fields = ['user', 'author']

    def to_representation(self, instance):
        return SubscriberDetailSerializer(instance, context=self.context).data

    def validate(self, data):
        request = self.context.get('request')
        author_id = (
            self.context.get('request').parser_context.get('kwargs').get('id')
        )
        author = get_object_or_404(User, id=author_id)
        if request.user == author:
            raise serializers.ValidationError(
                "You can't (un)subscribe to yourself"
            )
        if Follow.objects.filter(user=request.user, author=author).exists():
            raise serializers.ValidationError(
                'You already follow this user'
            )
        return data


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        request = self.context.get('request')
        recipe_pk = (
            self.context.get('request').parser_context.get('kwargs').get('pk')
        )
        recipe = get_object_or_404(Recipe, pk=recipe_pk)
        if ShoppingList.objects.filter(
            recipe=recipe,
            user=request.user
        ).exists():
            raise serializers.ValidationError(
                f'Recipe "{recipe.name}" was already added '
                'to shopping list.'
            )
        if Favorite.objects.filter(
            recipe=recipe,
            user=request.user
        ).exists():
            raise serializers.ValidationError(
                f'Recipe "{recipe.name}" was already added '
                'to favorites.'
            )
        return data
