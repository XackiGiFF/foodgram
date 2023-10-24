from django.contrib.admin import (ModelAdmin, TabularInline, action, register,
                                  site)
from django.utils.safestring import mark_safe

from .models import (AmountIngredient, Favorite, Ingredient, OrderCart, Recipe,
                     Tag)

site.site_header = 'Администрирование Foodgram'
EMPTY_VALUE_DISPLAY = 'Значение не указано'


class IngredientInline(TabularInline):
    model = AmountIngredient
    extra = 2


@register(AmountIngredient)
class AmountIngredientAdmin(ModelAdmin):
    list_display = ('id', 'recipe', 'ingredients',)


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = (
        'id', 'name', 'measurement_unit',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'name',
    )

    save_on_top = True
    empty_value_display = EMPTY_VALUE_DISPLAY


@action(description="Copy")
def duplicate_event(ModelAdmin, request, queryset):
    for object in queryset:
        object.id = None
        object.name = object.name + ' copy'
        object.save()


duplicate_event.short_description = "Дублировать выбранные рецепты"


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = (
        'name',
        'author',
        'get_image',
    )
    fields = (
        ('name', 'cooking_time',),
        ('author', 'tags',),
        ('text',),
        ('image',),
    )
    raw_id_fields = ('author',)
    search_fields = (
        'name', 'author', 'tags'
    )
    list_filter = (
        'name', 'author__username', 'tags',
    )

    inlines = (IngredientInline,)
    save_on_top = True
    empty_value_display = EMPTY_VALUE_DISPLAY
    actions = [duplicate_event]

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="80" height="30">')

    get_image.short_description = 'Изображение'


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = (
        'name', 'color', 'slug',
    )
    search_fields = (
        'name', 'color'
    )

    save_on_top = True
    empty_value_display = EMPTY_VALUE_DISPLAY


@register(OrderCart)
class OrderCartAdmin(ModelAdmin):
    list_fields = (
        'id', 'user', 'recipe'
    )
    search_fields = (
        'user', 'recipe'
    )

    save_on_top = True
    empty_value_display = EMPTY_VALUE_DISPLAY


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_fields = (
        'id', 'user', 'recipe',
    )
    search_fields = (
        'user', 'recipe',
    )

    save_on_top = True
    empty_value_display = EMPTY_VALUE_DISPLAY
