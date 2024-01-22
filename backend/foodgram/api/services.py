# from django.db.models import Sum
# from django.db.models.functions import Coalesce
# from recipes.models import Quantity


# def get_shopping_cart(request):
#     json = {}
#     user = request.user
#     quantities = (
#         Quantity.objects
#         .filter(recipe__author=user)
#         .values('ingredient__name', 'ingredient__measurement_unit')
#         .annotate(quantity=Coalesce(Sum('amount'), 0))
#     )
#     for quantity in quantities:
#         json[quantity['ingredient__name']] = {
#             'Количество': quantity['quantity'],
#             'Ед.изм.': quantity['ingredient__measurement_unit']
#         }
#     return json

from io import StringIO

from django.db.models import Sum

from recipes.models import Quantity


def get_shopping_cart(user):
    text_stream = StringIO()
    text_stream.write('Список покупок\n')
    text_stream.write('Ингредиент - Единица измерения - Количество\n')
    shopping_cart = (
        Quantity.objects.select_related('recipe', 'ingredient')
        .filter(recipe__recipes_shoppingcart_related__user=user)
        .values_list(
            'ingredient__name',
            'ingredient__measurement_unit')
        .annotate(amount=Sum('amount'))
        .order_by('ingredient__name')
    )
    lines = (' - '.join(str(field) for field in item) + '\n'
             for item in shopping_cart)
    text_stream.writelines(lines)
    return text_stream.getvalue()