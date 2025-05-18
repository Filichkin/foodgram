from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from recipes.models import Recipe

from api.serializers import FavoriteRecipeSerializer


class AddDeleteMixin:
    def add_to(self, model, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        serializer = FavoriteRecipeSerializer(
            recipe,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        model.objects.create(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, request, id):
        obj = model.objects.filter(recipe__id=id, user=request.user)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
