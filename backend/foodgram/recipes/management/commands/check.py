from django.core.management.base import BaseCommand
from recipes.models import Ingredient
import json
# import os
# from django.conf import settings


class Command(BaseCommand):
    help = 'Заполнение ингридиентов'

    def handle(self, *args, **options):
        with open('data/ingredients.json', 'r') as f:
            data = json.load(f)

        for i in data:
            igrd = Ingredient.objects.create(name=i['name'],
                                             measurement_unit=i['measurement_unit'])
            igrd.save()
        self.stdout.write(self.style.SUCCESS('Привет, это ваша команда!'))
