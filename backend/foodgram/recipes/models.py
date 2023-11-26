from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(verbose_name='Тэг',
                            max_length=200,
                            unique=True)
    color = models.CharField(verbose_name='Цветовой код',
                             max_length=10,
                             unique=True)
    slug = models.SlugField(max_length=200,
                            unique=True)

    def __str__(self):
        return self.name[:30]


class Ingredient(models.Model):
    name = models.CharField(verbose_name='Ингредиент',
                            max_length=200)
    measurement_unit = models.CharField(verbose_name='Единица измерения',
                                        max_length=17)

    def __str__(self):
        return self.name[:30]


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipe',
                               verbose_name='Автор')
    name = models.CharField(verbose_name='Название',
                            max_length=200)
    image = models.ImageField(
        'Картинка',
        upload_to='static/recipes',
        blank=True
    )
    text = models.TextField(help_text='Введите описание рецепта',
                            verbose_name='Описание рецепта')
    ingredients = models.ManyToManyField(Ingredient, related_name='recipe',
                                         verbose_name='Ингредиент')
    tags = models.ManyToManyField(Tag, related_name='recipe',
                                  verbose_name='Тэг')
    cooking_time = models.IntegerField(verbose_name='Время приготовления')

    def __str__(self):
        return self.name[:30]


class Quantity(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='quan_recipe',
                               verbose_name='Рецепт')
    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   related_name='quan_ingr',
                                   verbose_name='Ингредиент')
    amount = models.IntegerField(verbose_name='Количество')

    def __str__(self):
        return f'Количество {self.ingredient} в {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='favorites',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='favorites',
                               verbose_name='Рецепт')

    def __str__(self):
        return f'Избранные {self.recipe} у {self.user}'


class Shoppingcart(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='cart',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='cart',
                               verbose_name='Рецепт')

    def __str__(self):
        return f'В корзине {self.user} ингриедиеты для {self.recipe}'
