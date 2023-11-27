from djoser.serializers import UserCreateSerializer
from djoser.serializers import UserSerializer as UserHandleSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import SerializerMethodField
from rest_framework.status import HTTP_400_BAD_REQUEST

from users.models import Follow, User
from recipes.models import (Favorite, Ingredient, Quantity, Recipe,
                            ShoppingCart, Tag)


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


class UserSerializer(UserHandleSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')
        model = User

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user
        if current_user.is_authenticated:
            return Follow.objects.filter(
                user=current_user, following=obj.id).exists()
        return False


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'password',
        )


class FollowSerializer(UserSerializer):
    id = serializers.ReadOnlyField(source='user.id')
    email = serializers.ReadOnlyField(source='user.email')
    username = serializers.ReadOnlyField(source='user.username')
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = MiniRecipesSerializer(read_only=True, many=True)
    recipes_count = SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')
        model = User
        read_only_fields = ("all",)

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(user=obj.user,
                                     following=obj.following).exists()

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.user).count()

    def validate(self, obj):
        author = self.instance
        user = self.context.get('request').user
        if user == author:
            raise ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code=HTTP_400_BAD_REQUEST
            )
        return obj

    def create(self, validated_data):
        user = self.context['request'].user
        following_user = self.instance
        follow = Follow.objects.create(user=user, following=following_user)
        return follow


class MaxiIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    unit = serializers.ReadOnlyField(source='ingredient.unit')

    class Meta:
        fields = ('id', 'name', 'unit', 'amount')
        model = Quantity


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
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
            return Favorite.objects.filter(user=current_user,
                                           recipe=obj.id).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        cart_user = self.context['request'].user
        if cart_user.is_authenticated:
            return ShoppingCart.objects.filter(user=cart_user,
                                               recipe=obj.id).exists()
        return False

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('recipe', [])

        validated_data['author'] = self.context['request'].user
        recipe = Recipe(**validated_data)
        recipe.save()

        tags = [Tag.objects.get_or_create(**tag_data)[0]
                for tag_data in tags_data]
        recipe.tags.set(tags)

        for ingredient_data in ingredients_data:
            ingredient, created = Ingredient.objects.get_or_create(
                **ingredient_data['ingredient'])
            quantity, created = Quantity.objects.update_or_create(
                recipe=recipe, ingredient=ingredient, defaults=ingredient_data
            )

        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('recipe', [])

        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)

        tags = [Tag.objects.get_or_create(**tag_data)[0]
                for tag_data in tags_data]
        instance.tags.set(tags)

        for ingredient_data in ingredients_data:
            ingredient, created = Ingredient.objects.get_or_create(
                **ingredient_data['ingredient'])
            quantity, created = Quantity.objects.update_or_create(
                recipe=instance, ingredient=ingredient,
                defaults=ingredient_data)

        instance.save()
        return instance


class FavoriteSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all(),
                                            write_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault(),
                                   required=False)
    name = serializers.CharField(source='recipe.name', read_only=True)
    image = serializers.ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.DurationField(source='recipe.cooking_time',
                                             read_only=True)

    def create(self, validated_data):
        user = validated_data.get('user', self.context['request'].user)
        recipe = validated_data['id']
        favorite, created = Favorite.objects.get_or_create(user=user,
                                                           recipe=recipe)
        return favorite

    def delete(self, validated_data):
        user = validated_data.get('user', self.context['request'].user)
        recipe = validated_data['id']
        favorite = Favorite.objects.get(user=user, recipe=recipe)
        favorite.delete()


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault(),
                                   required=False)

    class Meta:
        fields = '__all__'
        model = ShoppingCart

    def to_representation(self, data):
        return MiniRecipesSerializer(
            data, context={'request': self.context.get('request')}).data
