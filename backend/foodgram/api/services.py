from recipes.models import Shoppingcart


def shoppingcart(request):
    json = {}
    user = request.user
    shopping_recipe = Shoppingcart.objects.filter(user=user).all()
    for recipe in shopping_recipe:
        ingredients = recipe.recipe.ingredients.all()
        for ingredient in ingredients:
            json[ingredient.name] = ''
        # for ingredient in ingredients:
        #     json[ingredient.unit] = ''
           
