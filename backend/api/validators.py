"""Модуль валидации
"""
from string import hexdigits

from api.manager.conf import MAX_COLOR_LEN, MIN_COLOR_LEN
from rest_framework.serializers import ValidationError


def hex_color_validate(value):
    """Проверяет - может ли значение быть шестнадцатеричным цветом.

    Args:
        value (str):
            Значение переданное для проверки.

    Raises:
        ValidationError:
            Переданное значение не корректной длины.
        ValidationError:
            Символы значения выходят за пределы 16-ричной системы.
    """
    if len(value) not in (MIN_COLOR_LEN, MAX_COLOR_LEN):
        raise ValidationError(
            f'{value} не правильной длины ({len(value)}).'
        )
    if not set(value).issubset(hexdigits):
        raise ValidationError(
            f'{value} не шестнадцатиричное.'
        )


def search_duplications(array, key, value):
    verbose_data = sum(map(list, map(dict.items, array)), [])
    return (key, value) in verbose_data


# Словарь для сопостановления латинской и русской стандартных раскладок.
incorrect_layout = str.maketrans(
    'qwertyuiop[]asdfghjkl;\'zxcvbnm,./',
    'йцукенгшщзхъфывапролджэячсмитьбю.'
)
