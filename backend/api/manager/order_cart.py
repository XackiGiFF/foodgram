from datetime import datetime as dt

from django.db.models import F, Sum
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from recipes.models import AmountIngredient
from .conf import DATE_TIME_FORMAT


def download_cart(user):
    """
    Формирует будущий файл *.txt со списком покупок.

    Считает сумму ингредиентов в рецептах выбранных для покупки.
    Возвращает текстовый файл со списком ингредиентов.
    Вызов метода через url:  */recipe/<int:id>/download_shopping_cart/.
    Args:
        user (User): Пользователь.

    Returns:
        String: Ответ с текстовым файлом.
    """
    if not user.shoppingcart.exists():
        return Response(status=HTTP_400_BAD_REQUEST)
    ingredients = AmountIngredient.objects.filter(
        recipe__shoppingcart__user_id=user).values(
        ingredient=F('ingredients__name'),
        measure=F('ingredients__measurement_unit')).order_by(
        'ingredients__name').annotate(amount=Sum('amount'))

    shopping_list = (
        f'Список покупок для:\n\n'
        f'{user.username} ({user.first_name} {user.last_name})\n\n'
        f'{dt.now().strftime(DATE_TIME_FORMAT)}\n\n'
    )
    for ing in ingredients:
        shopping_list += (
            f'{ing["ingredient"]}: {ing["amount"]} {ing["measure"]}\n'
        )

    shopping_list += '\n\nПосчитано в Foodgram'

    return shopping_list
