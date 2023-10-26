from django.core.management.base import BaseCommand
from recipes.models import Shoppingcart
# import os
# from django.conf import settings


class Command(BaseCommand):
    help = 'Описание вашей команды'

    def handle(self, *args, **options):
        json = {}
        shopping_recipe = Shoppingcart.objects.filter(user=4).all()
        for recipe in shopping_recipe:

            quantity = recipe.recipe.quan_recipe.all()

            for a in quantity:
                print(a.ingredient.name, a.amount, a.ingredient.unit)
                dict_amount = 0
                if a.ingredient.name in json:
                    dict_amount = json[a.ingredient.name]['Количество']

                json[a.ingredient.name] = {'Количество':
                                           a.amount + dict_amount,
                                           'Ед.изм.': a.ingredient.unit}
                print(json)
        self.stdout.write(self.style.SUCCESS('Привет, это ваша команда!'))
