import csv
import json
import os
from string import hexdigits

from recipes.models import Ingredient, Tag
from rest_framework.serializers import ValidationError

TAGS_MANAGER = 'tags'

PRODUCT_MANAGER = 'product'

JSON_READER = '.json'

CSV_READER = '.csv'


def default():
    print('Файл должен быть json|csv формата!')


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
    if len(value) not in (3, 6):
        raise ValidationError(
            f'{value} не правильной длины ({len(value)}).'
        )
    if not set(value).issubset(hexdigits):
        raise ValidationError(
            f'{value} не шестнадцатиричное.'
        )


def check_color(color):
    """Проверяет и нормализует код цвета.

    Args:
        color (str): Строка описывающая код цвета.

    Returns:
        str: Проверенная строка описывающая цвет в HEX-формате (#12AB98).
    """
    color = str(color).strip(' #')
    hex_color_validate(color)
    return f'#{color}'


class FileReader:

    def __init__(self, file, manager):
        self.file = file
        self.reader = os.path.splitext(self.file.name)[1]
        self.manager = manager

    def tags_csv(self):
        datareader = csv.reader(self.file)
        for row in datareader:
            try:
                Tag.objects.get_or_create(
                    name=row[0],
                    color=row[1],
                    slug=row[2]
                )
                print(f'{row[0]} записан в базу')
            except Exception as error:
                print(f'Ошибка при добавлении {row[0]} в базу.\n'
                      f'Ошибка: {error}')
        self.file.close()

    def tags_json(self):
        data = json.load(self.file)
        for row in data:
            try:
                Tag.objects.get_or_create(
                    name=row["name"],
                    color=row["color"],
                    slug=row["slug"]
                )
                print(f'{row["name"]} записан в базу')
            except Exception as error:
                name = row["name"]
                print(f'Ошибка при добавлении {name} в базу.\n'
                      f'Ошибка: {error}')
        self.file.close()

    def product_csv(self):
        datareader = csv.reader(self.file)
        for row in datareader:
            try:
                Ingredient.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1],
                )
                print(f'{row[0]} записан в базу')
            except Exception as error:
                print(f'Ошибка при добавлении {row[0]} в базу.\n'
                      f'Ошибка: {error}')
        self.file.close()

    def product_json(self):
        data = json.load(self.file)
        for row in data:
            try:
                Ingredient.objects.get_or_create(
                    name=row["name"],
                    measurement_unit=row["measurement_unit"],
                )
                print(f'{row["name"]} записан в базу')
            except Exception as error:
                name = row["name"]
                print(f'Ошибка при добавлении {name} в базу.\n'
                      f'Ошибка: {error}')
        self.file.close()

    def read_file(self):
        if self.reader not in (CSV_READER, PRODUCT_MANAGER):
            default()
            return
        if self.reader == CSV_READER:
            if self.manager == TAGS_MANAGER:
                self.tags_csv()
                return
            if self.manager == PRODUCT_MANAGER:
                self.product_csv()
                return
        if self.reader == JSON_READER:
            if self.manager == TAGS_MANAGER:
                self.tags_json()
                return
            if self.manager == PRODUCT_MANAGER:
                self.product_json()
                return
