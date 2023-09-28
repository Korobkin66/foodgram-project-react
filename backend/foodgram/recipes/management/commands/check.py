from django.core.management.base import BaseCommand
from recipes.models import Shoppingcart
# import os
# from django.conf import settings


class Command(BaseCommand):
    help = 'Описание вашей команды'

    def handle(self, *args, **options):
        shopping_recipe = Shoppingcart.objects.filter(user=4).all()
        for recipe in shopping_recipe:
            ingredients = recipe.recipe.ingredients.all()
            for i in ingredients:
                # am = i.vol_ingr
                print(i.name, i.unit)
                print(i.vol_ingr.amount)

        self.stdout.write(self.style.SUCCESS('Привет, это ваша команда!'))
