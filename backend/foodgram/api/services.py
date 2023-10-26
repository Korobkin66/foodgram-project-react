from recipes.models import Shoppingcart


def shoppingcart(request):
    json = {}
    user = request.user
    shopping_recipe = Shoppingcart.objects.filter(user=user).all()
    for recipe in shopping_recipe:
        quantity = recipe.recipe.quan_recipe.all()
        for a in quantity:
            print(a.ingredient.name, a.amount, a.ingredient.unit)
            d_amount = 0
            if a.ingredient.name in json:
                d_amount = json[a.ingredient.name]['Количество']
            json[a.ingredient.name] = {'Количество': a.amount +
                                       d_amount, 'Ед.изм.': a.ingredient.unit}
    return json
