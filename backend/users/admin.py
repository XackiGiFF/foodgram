from django.contrib.admin import ModelAdmin, register
from django.contrib.auth.admin import UserAdmin

from recipes.admin import EMPTY_VALUE_DISPLAY

from .models import Subscribe, User


@register(User)
class MyUserAdmin(UserAdmin):
    list_display = (
        'username', 'first_name', 'last_name', 'email',
    )
    fields = (
        ('username', 'email',),
        ('first_name', 'last_name',),
    )
    fieldsets = []

    search_fields = (
        'username', 'email',
    )
    list_filter = (
        'first_name', 'email',
    )
    save_on_top = True


@register(Subscribe)
class SubscribeAdmin(ModelAdmin):
    list_display = (
        'user', 'author'
    )

    save_on_top = True
    empty_value_display = EMPTY_VALUE_DISPLAY
