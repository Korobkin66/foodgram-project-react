from django.contrib import admin

from .models import Favorite, Ingredient, Quantity, Recipe, Shoppingcart, Tag


class RecipeAdmin(admin.ModelAdmin):

    list_display = (
        'pk',
        'name',
        'author',
        'favorites'
    )
    list_filter = ('name',
                   'author',
                   'tags')
    empty_value_display = '-пусто-'
    readonly_fields = ['favorites']

    @admin.display(description='Избранное')
    def favorites(self, obj):
        return obj.favorites.count()


class IngredientAdmin(admin.ModelAdmin):

    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)
    empty_value_display = '-пусто-'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Quantity)
admin.site.register(Favorite)
admin.site.register(Shoppingcart)
