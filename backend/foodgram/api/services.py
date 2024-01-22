from django.db.models import Sum
from django.db.models.functions import Coalesce
from recipes.models import Quantity


def get_shopping_cart(request):
    json = {}
    user = request.user
    quantities = (
        Quantity.objects
        .filter(recipe__author=user)
        .values('ingredient__name', 'ingredient__measurement_unit')
        .annotate(quantity=Coalesce(Sum('amount'), 0))
    )
    for quantity in quantities:
        ingredient_name = quantity['ingredient__name']
        measurement_unit = quantity['ingredient__measurement_unit']
        if ingredient_name not in json:
            json[ingredient_name] = {
                'Количество': quantity['quantity'],
                'Ед.изм.': measurement_unit
            }
        else:
            json[ingredient_name]['Количество'] += quantity['quantity']

    return json
