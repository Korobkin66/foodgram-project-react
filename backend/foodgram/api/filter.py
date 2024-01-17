from django.contrib.auth import get_user_model
from django_filters import FilterSet, CharFilter, filters

import logging

from recipes.models import Recipe, Tag, Ingredient
from users.models import User

logger = logging.getLogger(__name__)


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(field_name='is_in_shopping_cart', lookup_expr='exact')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        logger.info('queryset_favorite', queryset)
        logger.info('value', value)
        if self.request.user.is_authenticated:  # and value:
            logger.info('попался!')
            return queryset.filter(favorites__user=self.request.user)
        return queryset
    
    def get_is_in_shopping_cart(self, queryset, name, value):
        logger.info('queryset_shopcart', queryset)
        if self.request.user.is_authenticated:  # and value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ['name']