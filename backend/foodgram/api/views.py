from datetime import datetime
from django.http import HttpResponse
from django.utils.text import slugify
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_400_BAD_REQUEST)

from users.models import Follow, User
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, FollowSerializer,
                          IngredientSerializer, BaseUserSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          SubscribeSerializer,
                          TagSerializer, MiniRecipesSerializer)
from .pagination import MyPagination
from .services import get_shopping_cart
from .filter import RecipeFilter, IngredientFilter


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = BaseUserSerializer
    pagination_class = MyPagination

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id):
        user = request.user
        follow_author = get_object_or_404(User, id=id)
        follow_instance, created = Follow.objects.get_or_create(
            user=user, following=follow_author)
        if request.method == 'POST':
            serializer = SubscribeSerializer(data=request.data,
                                             instance=follow_author,
                                             context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)

        if Follow.objects.filter(user=user, following=follow_author).exists():
            Follow.objects.filter(user=user, following=follow_author).delete()
            return Response({"log": "Вы отписались"}, status=HTTP_200_OK)
        return Response({"log": "Вы не подписаны на пользователя"},
                        status=HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='subscriptions',
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request, id=None):
        queryset = Follow.objects.filter(user=request.user)
        followed_users = queryset.values_list('following', flat=True)
        users = User.objects.filter(id__in=followed_users)

        print("Followed users:", followed_users)
        print("Users:", users)

        data = self.paginate_queryset(users)
        serializer = FollowSerializer(data, many=True,
                                      context={'request': request})
        
        response_data = serializer.data

        # Добавим отладочное сообщение для сериализированных данных
        print("Serialized data:", response_data)

        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = IngredientFilter
    filter_backends = (DjangoFilterBackend, )
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes_by_action = {
        'create': [IsAuthorOrReadOnly, IsAdminOrReadOnly],
        'partial_update': [IsAuthorOrReadOnly, IsAdminOrReadOnly],
        'destroy': [IsAuthorOrReadOnly, IsAdminOrReadOnly]}
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend, )
    pagination_class = MyPagination

    def fav_or_shop_metod(self, request, pk, model, serializer_class):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            serializer = serializer_class(data={
                'id': recipe.id,
                'recipe': recipe.id,
                'user': user},
                context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response_data = serializer.data
            status_code = HTTP_201_CREATED
        else:
            if model.objects.filter(user=user, recipe=recipe).exists():
                model.objects.filter(user=user, recipe=recipe).delete()
                response_data = {"log": "Рецепт успешно удален из списка."}
            else:
                response_data = {"log": "В списке отсутствует данный рецепт."}
            status_code = HTTP_200_OK

        return Response(response_data, status=status_code)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        return self.fav_or_shop_metod(request, pk, Favorite,
                                      FavoriteSerializer)
        serializer = MiniRecipesSerializer(recipe)
        return Response(serializer.data, status=HTTP_201_CREATED)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk):
        return self.fav_or_shop_metod(request, pk, ShoppingCart,
                                      ShoppingCartSerializer)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"log": "Рецепт успешно удален"}, status=HTTP_200_OK)

    @action(detail=False,
            methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        txt_content = get_shopping_cart(self, request)
        if txt_content is None:
            return Response('Корзина пуста.', status=HTTP_200_OK)
        date = datetime.now().strftime('%Y%m%d_%H%M%S')
        txt_filename = (f'shopping_cart_'
                        f'{slugify(request.user.username)}_{date}.txt')
        response = HttpResponse(
            txt_content, content_type='text/plain')
        response['Content-Disposition'] = (
            f'attachment; filename="{txt_filename}"')
        return response
