# from django.db.models import Sum

# from recipes.models import Quantity


# def get_shopping_cart(request):
#     json = {}
#     user = request.user
#     quantities = (
#         Quantity.objects
#         .filter(recipe__author=user)
#         .values('ingredient__name', 'ingredient__measurement_unit')
#         .annotate(quantity=Sum('amount')))
#     for quantity in quantities:
#         json[quantity['ingredient__name']] = {
#             'Количество': quantity['quantity'],
#             'Ед.изм.': quantity['ingredient__measurement_unit']}
#     return json

from django.contrib.auth import get_user_model
from django.db.models import Sum

from recipes.models import RecipeIngredient

User = get_user_model()


def get_shopping_cart(self, request):
    """ Функция для скачивания списка покупок. """

    ingredients_data = RecipeIngredient.objects.values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(total_ingredients=Sum('amount')).order_by('ingredient__name')

    txt_content = 'Список ингредиентов для покупки:\n\n'

    for item in ingredients_data:
        ingredient_name = item.get('ingredient__name')
        measurement_unit = item.get('ingredient__measurement_unit')
        tolal_amount = item.get('total_ingredients')

        txt_content += (f'{ingredient_name.capitalize()} -- {tolal_amount}'
                        f' {measurement_unit}.\n')

    return txt_content
