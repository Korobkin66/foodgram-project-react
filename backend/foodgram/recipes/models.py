from django.db import models
from django.core.validators import MinValueValidator
from django.db.models.constraints import UniqueConstraint

from users.models import User

MAX_NUMB_OF_CHAR = 200
MAX_LENGTH_COLOR_CODE = 10
MAX_LENGTH_UNIT = 17


class Tag(models.Model):
    name = models.CharField(verbose_name='Тэг',
                            max_length=MAX_NUMB_OF_CHAR,
                            unique=True)
    color = models.CharField(verbose_name='Цветовой код',
                             max_length=MAX_LENGTH_COLOR_CODE,
                             unique=True)
    slug = models.SlugField(max_length=MAX_NUMB_OF_CHAR,
                            unique=True)

    def __str__(self):
        return self.name[:30]


class Ingredient(models.Model):
    name = models.CharField(verbose_name='Ингредиент',
                            max_length=MAX_NUMB_OF_CHAR)
    measurement_unit = models.CharField(verbose_name='Единица измерения',
                                        max_length=MAX_LENGTH_UNIT)

    def __str__(self):
        return self.name[:30]


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Автор')
    name = models.CharField(verbose_name='Название',
                            max_length=MAX_NUMB_OF_CHAR)
    image = models.ImageField(
        'Картинка',
        upload_to='static/recipes',
        blank=True
    )
    text = models.TextField(help_text='Введите описание рецепта',
                            verbose_name='Описание рецепта')
    # ingredients = models.ManyToManyField(Ingredient, related_name='recipes',
    #                                      verbose_name='Ингредиент')
    quantities = models.ManyToManyField('Quantity', related_name='recipes',
                                        verbose_name='Количество ингредиентов')
    tags = models.ManyToManyField(Tag, related_name='recipes',
                                  verbose_name='Тэг')
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(0)])

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

    class Meta:
        constraints = [
            UniqueConstraint(fields=['recipe', 'ingredient'],
                             name='unique_quantity')]

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

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'recipe'],
                             name='unique_favorite')]

    def __str__(self):
        return f'Избранные {self.recipe} у {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='cart',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='cart',
                               verbose_name='Рецепт')

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'recipe'],
                             name='unique_shopping_cart')]

    def __str__(self):
        return f'В корзине {self.user} ингриедиеты для {self.recipe}'
