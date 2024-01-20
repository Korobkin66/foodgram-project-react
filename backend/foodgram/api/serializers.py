import logging
from drf_extra_fields.fields import Base64ImageField
from django.db import transaction
from django.db.models import F
from djoser.serializers import UserCreateSerializer
from djoser.serializers import UserSerializer as UserHandleSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import SerializerMethodField
from rest_framework.status import HTTP_400_BAD_REQUEST

from users.models import Follow, User
from recipes.models import (Favorite, Ingredient, Quantity, Recipe,
                            ShoppingCart, Tag)

logger = logging.getLogger(__name__)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        read_only_fields = ("__all__",)
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        read_only_fields = ("__all__",)
        model = Ingredient


class MiniRecipesSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class BaseUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')
        model = User

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user
        if current_user.is_authenticated:
            return Follow.objects.filter(user=current_user,
                                         following=obj.id).exists()
        return False


class UserSerializer(UserHandleSerializer):
    class Meta(BaseUserSerializer.Meta):
        pass


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'password',
        )


class FollowSerializer(BaseUserSerializer):
    recipes = MiniRecipesSerializer(read_only=True, many=True)
    recipes_count = SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def validate(self, obj):
        author = self.instance
        user = self.context.get('request').user
        if user == author:
            raise ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code=HTTP_400_BAD_REQUEST
            )
        return obj


class MaxiIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = Quantity


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = BaseUserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image =  Base64ImageField()

    def get_ingredients(self, obj) :
        ingredients = obj.ingredients.values(
            "id", "name", "measurement_unit", amount=F("quan_ingr__amount")
        )
        logger.info(f'ingredients {ingredients}')  #ingredients
        return ingredients

    def validate(self, data):
        validated_data = super().validate(data)
        recipe = validated_data.get('recipes', [])
        tags = self.initial_data.get("tags")
        ingredients = self.initial_data.get("ingredients")
        logger.info(f'ingredients_val {ingredients}')  #ingredients_val
        ingredient_names = set()
        for ingredient_data in recipe:
            ingredient_name = ingredient_data['ingredient']['name']
            if ingredient_name in ingredient_names:
                raise serializers.ValidationError(
                    f"Ингредиент '{ingredient_name}' уже добавлен в рецепт.")
            ingredient_names.add(ingredient_name)
        validated_data.update(
            {
                "tags": tags,
                "ingredients": ingredients
            }
        )
        logger.info(f'validated_data_val {validated_data}')  #validated_data_val
        return validated_data

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

    def process_tags_and_ings(self, instance, tags_data, ingredients_data):
        with transaction.atomic():
            tags = [Tag.objects.get(id=tag_id) for tag_id in tags_data]
            instance.tags.set(tags)

            # ingredients = []
            # for ingredient_data in ingredients_data:
            #     # ingredient_id = ingredient_data.get('id')
            #     ingredient_id = ingredient_data.get('ingredient', {}).get('id') # attempt
            #     amount = ingredient_data.get('amount')
            #     ingredient = Ingredient.objects.get(ingredient__id=ingredient_id)
            #     ingredients.append(Quantity(recipe=instance,
            #                                 ingredient=ingredient,
            #                                 amount=amount))
            # logger.info(f'ingredients_data {ingredients_data}')
            # Quantity.objects.bulk_create(ingredients)

            ingredients = []
            for ingredient_data in ingredients_data:
                # ingredient_id = ingredient_data.get('id')
                ingredient_id = ingredient_data.get('id') # attempt
                logger.info(f'ingredient_data_ID {ingredients_data}') #ingredient_data_ID
                amount = ingredient_data.get('amount')
                ingredient = Ingredient.objects.get(id=ingredient_id)
                ingredients.append(Quantity(recipe=instance,
                                            ingredient=ingredient,
                                            amount=amount))
            logger.info(f'ingredients_data {ingredients_data}') #ingredients_data
            Quantity.objects.bulk_create(ingredients)

    @transaction.atomic
    def create(self, validated_data):
        logger.info(f'validated_data {validated_data}')  #validated_data
        # logger.info(f'self {self}')  #self
        tags_data = validated_data.pop('tags', [])
        logger.info(f'tags_data {tags_data}')  #tags_data
        ingredients_data = validated_data.pop('ingredients', [])
        validated_data['author'] = self.context['request'].user
        logger.info(f'ingredients_data {ingredients_data}')  #ingredients_data
        recipe = Recipe.objects.create(**validated_data)
        logger.info(f'recipe_update {recipe}')  #recipe
        self.process_tags_and_ings(recipe, tags_data, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        logger.info(f'instance_update {instance}')  #instance_update
        logger.info(f'validated_data_update {validated_data}')  #validated_data_update
        tags_data = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('ingredients', [])
        logger.info(f'ingredients_data_udate {ingredients_data}')  #ingredients_data_udate
        self.process_tags_and_ings(instance, tags_data, ingredients_data)
        super().update(instance, validated_data)
        logger.info(f'instance_update {instance}')
        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all(),
                                            write_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault(),
                                   required=False)
    name = serializers.CharField(source='recipes.name', read_only=True)
    image = serializers.ImageField(source='recipes.image', read_only=True)
    cooking_time = serializers.DurationField(source='recipes.cooking_time',
                                             read_only=True)

    def create(self, validated_data):
        user = validated_data.get('user', self.context['request'].user)
        recipe_id = validated_data['id'].id
        recipe = Recipe.objects.get(id=recipe_id)
        favorite, created = Favorite.objects.get_or_create(user=user,
                                                           recipe=recipe)
        return favorite

    def delete(self, validated_data):
        user = validated_data.get('user', self.context['request'].user)
        recipe_id = validated_data['id'].id
        recipe = Recipe.objects.get(id=recipe_id)
        favorite = Favorite.objects.get(user=user, recipe=recipe)
        favorite.delete()
    
    class Meta:
        fields = '__all__'
        model = Favorite


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault(),
                                   required=False)
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        fields = '__all__'
        model = ShoppingCart

    def to_representation(self, data):
        return MiniRecipesSerializer(
            data.recipe, context={'request': self.context.get('request')}).data
