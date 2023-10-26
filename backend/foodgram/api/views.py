from django.shortcuts import render, get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_400_BAD_REQUEST)

from recipes.models import Favorite, Tag, Shoppingcart, Ingredient, Recipe
from .permissions import IsAuthorOrReadOnly, IsAdminOrReadOnly
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeSerializer, MiniRecipesSerializer,
                          ShoppingcartSerializer)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAdminOrReadOnly]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrReadOnly, IsAdminOrReadOnly]

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsAuthenticated])
    def recipe_fav(self, request, pk):
        user = request.user
        if Favorite.objects.filter(user=user, recipe=pk).exists():
            return Response({"error": "уже в Избранном"},
                            status=HTTP_400_BAD_REQUEST)
        Favorite.objects.create(user=user, recipe=pk)
        fav_recipe = get_object_or_404(Recipe, id=pk)
        serializer = MiniRecipesSerializer(fav_recipe)
        return Response(serializer.data, status=HTTP_201_CREATED)

    @action(detail=True, methods=['delete'],
            permission_classes=[permissions.IsAuthenticated])
    def recipe_unfav(self, request, pk):
        user = request.user
        if Favorite.objects.filter(user=user, recipe=pk).exists():
            Favorite.objects.filter(user=user, recipe=pk).delete()
            return Response(status=HTTP_200_OK)
        return Response({"error": "not in Favorites"},
                        status=HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsAuthenticated])
    def shop_cart_add(self, request, pk):
        user = request.user
        if Shoppingcart.objects.filter(user=user, recipe=pk).exists():
            return Response({"error": "уже в Корзине"},
                            status=HTTP_400_BAD_REQUEST)
        Shoppingcart.objects.create(user=user, recipe=pk)
        shop_cart = get_object_or_404(Recipe, id=pk)
        serializer = ShoppingcartSerializer(shop_cart)
        return Response(serializer.data, status=HTTP_201_CREATED)
 
    @action(detail=True, methods=['delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shop_cart_del(self, request, pk):
        user = request.user
        if Shoppingcart.objects.filter(user=user, recipe=pk).exists():
            Shoppingcart.objects.filter(user=user, recipe=pk).delete()
            return Response(status=HTTP_200_OK)
        return Response({"error": "not in Shopping Cart"},
                        status=HTTP_400_BAD_REQUEST)
