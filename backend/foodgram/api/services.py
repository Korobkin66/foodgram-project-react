from django.db.models import Sum

from recipes.models import Quantity, ShoppingCart


def get_shopping_cart(self, request):
    shopping_cart = ShoppingCart.objects.filter(user=request.user)
    ingredients_data = Quantity.objects.filter(
        recipe__cart__in=shopping_cart).values(
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
