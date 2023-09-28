from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import SerializerMethodField, ReadOnlyField
from djoser.serializers import UserSerializer as UserHandleSerializer
from recipes.models import (Tag, Ingredient, Recipe,
                            Quantity, Shoppingcart, Favorite)
from users.models import Follow, User


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Ingredient


class MiniRecipesSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class FollowSerializer(serializers.ModelSerializer):
    recipes = MiniRecipesSerializer(read_only=True, many=True)
    recipes_count = SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        model = User

    def get_recipes_count(self, obj):
        return obj.recipe.count()


class UserSerializer(UserHandleSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')
        model = User

    def get_is_subscribed(self, obj):
        current_user = self.context['request'].user
        if current_user.is_authenticated:
            return Follow.objects.filter(
                user=current_user, following=obj.id).exists
        return False


class MaxiIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    unit = serializers.ReadOnlyField(source='ingredient.unit')

    class Meta:
        fields = ('id', 'name', 'unit', 'amount')
        model = Quantity


class RecipesSerializer(serializers.ModelSerializer):
    tag = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = MaxiIngredientSerializer(read_only=True, many=True,
                                           source='recipe')
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        model = Recipe

    def get_is_favorited(self, obj):
        current_user = self.context['request'].user
        if current_user.is_authenticated:
            return Favorite.objects.filter(
                user=current_user, recipe=obj.id).exists
        return False

    def get_is_in_shopping_cart(self, obj):
        cart_user = self.context['request'].user
        if cart_user.is_authenticated:
            return Shoppingcart.objects.filter(
                user=cart_user, recipe=obj.id).exists
        return False


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class ShoppingcartSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Shoppingcart

    def to_representation(self, data):
        return MiniRecipesSerializer(data.recipe,
                                     context={'request':
                                              self.context['request']}).data
