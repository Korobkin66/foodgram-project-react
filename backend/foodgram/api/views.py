from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_400_BAD_REQUEST)
from users.models import Follow, User

from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, FollowSerializer,
                          IngredientSerializer, MiniRecipesSerializer,
                          RecipeSerializer, ShoppingcartSerializer,
                          TagSerializer, UserSerializer)
from .services import get_shopping_cart


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id):
        user = request.user
        follow_author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = FollowSerializer(follow_author, data=request.data,
                                          context={"request": request})
            serializer.is_valid()

            Follow.objects.create(user=user, following=follow_author)
            return Response(serializer.data, status=HTTP_201_CREATED)
        if Follow.objects.filter(user=user,
                                    following=follow_author).exists():
            Follow.objects.filter(user=user,
                                    following=follow_author).delete()
            return Response({"log": "Вы отписались"}, status=HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='subscriptions',
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request, id=None):
        queryset = Follow.objects.filter(user=request.user)
        serializer = FollowSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data, status=HTTP_200_OK)


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
    permission_classes_by_action = {
        'create': [IsAuthorOrReadOnly, IsAdminOrReadOnly],
        'partial_update': [IsAuthorOrReadOnly, IsAdminOrReadOnly],
        'destroy': [IsAuthorOrReadOnly, IsAdminOrReadOnly]}

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            serializer = FavoriteSerializer(recipe, data=request.data,
                                            context={"request": request})
            serializer.is_valid()

            Favorite.objects.create(user=user, recipe=recipe)
            serializer = MiniRecipesSerializer(recipe)
            return Response(serializer.data, status=HTTP_201_CREATED)
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            Favorite.objects.filter(user=user, recipe=recipe).delete()
            return Response({"log": "Вы удалили рецепт из Избранного"},
                            status=HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response({"error": "уже в Корзине"},
                                status=HTTP_400_BAD_REQUEST)

            serializer = ShoppingcartSerializer(recipe, data=request.data,
                                                context={"request": request})
            serializer.is_valid()

            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = ShoppingcartSerializer(recipe)
            return Response(serializer.data, status=HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
                return Response({"log": "Вы удалили рецепт из Списка покупок"},
                                status=HTTP_200_OK)
            return Response({"error": "not in Shopping Cart"},
                            status=HTTP_400_BAD_REQUEST)

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save(author=request.user)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data,
    #                     status=HTTP_201_CREATED, headers=headers)

    # def partial_update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance,
    #                                      data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"log": "Рецепт успешно удален"}, status=HTTP_200_OK)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        shoping_cart = get_shopping_cart(request)
        response = HttpResponse(shoping_cart,
                                content_type="text.txt; charset=utf-8")
        filename = 'loaded_ingr.txt'
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response
