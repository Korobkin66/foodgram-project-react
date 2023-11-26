import json

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Заполнение ингредиентов'

    def handle(self, *args, **options):
        with open('data/ingredients.json', 'r') as f:
            data = json.load(f)

        mu = 'measurement_unit'

        for i in data:
            igrd = Ingredient.objects.create(name=i['name'],
                                             measurement_unit=i[mu])
            igrd.save()
        self.stdout.write(self.style.SUCCESS('Привет, это ваша команда!'))
