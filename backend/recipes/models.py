"""Модуль для создания, настройки и управления моделями пакета `recipe`.

Models:
    Recipe:
        Основная модель приложения, через которую описываются рецепты.
    Tag:
       Модель для группировки рецептов по тэгам.
       Связана с Recipe через Many-To-Many.
    Ingredient:
        Модель для описания ингредиентов.
        Связана с Recipe через модель AmountIngredient (Many-To-Many).
    AmountIngredient:
        Модель для связи Ingredient и Recipe.
        Также указывает количество ингридиента.
"""
from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import (CASCADE, CharField, CheckConstraint,
                              DateTimeField, ForeignKey, ImageField,
                              ManyToManyField, Model,
                              PositiveSmallIntegerField, Q, TextField,
                              UniqueConstraint)
from django.db.models.functions import Length

from recipes.manager.conf import (MAX_AMOUNT_INGREDIENT,
                                  MAX_LEN_RECIPES_CHARFIELD,
                                  MAX_LEN_RECIPES_TEXTFIELD, MAX_VALUE_COOKING,
                                  MIN_AMOUNT_INGREDIENT, MIN_VALUE_COOKING)
from users.models import User

CharField.register_lookup(Length)


class Tag(Model):
    """Тэги для рецептов.

    Связано с моделью Recipe через М2М.
    Поля `name` и 'slug` - обязательны для заполнения.

    Attributes:
        name(str):
            Название тэга. Установлены ограничения по длине и уникальности.
        color(str):
            Цвет тэга в HEX-кодировке. По умолчанию - чёрный
        slug(str):
            Те же правила, что и для атрибута `name`, но для корректной работы
            с фронтэндом следует заполнять латинскими буквами.

    Example:
        Tag('Завтрак', '01AB89', 'breakfast')
        Tag('Ланч', '01AB89', 'lanch')
    """
    name = CharField(
        verbose_name='Тэг',
        max_length=MAX_LEN_RECIPES_CHARFIELD,
        unique=True,
    )
    color = ColorField(verbose_name='Укажите HEX-код цвета', default='#FFFFFF')
    slug = CharField(
        verbose_name='Слаг тэга',
        max_length=MAX_LEN_RECIPES_CHARFIELD,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)
        constraints = (
            CheckConstraint(
                check=Q(name__length__gt=0),
                name='\n%(app_label)s_%(class)s_name is empty\n',
            ),
            CheckConstraint(
                check=Q(color__length__gt=0),
                name='\n%(app_label)s_%(class)s_color is empty\n',
            ),
            CheckConstraint(
                check=Q(slug__length__gt=0),
                name='\n%(app_label)s_%(class)s_slug is empty\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.name} (цвет: {self.color})'


class Ingredient(Model):
    """Ингридиенты для рецепта.

    Связано с моделью Recipe через М2М (AmountIngredient).

    Attributes:
        name(str):
            Название ингридиента.
            Установлены ограничения по длине и уникальности.
        measurement_unit(str):
            Единицы измерения ингридентов (граммы, штуки, литры и т.п.).
            Установлены ограничения по длине.
    """
    name = CharField(
        verbose_name='Ингридиент',
        max_length=MAX_LEN_RECIPES_CHARFIELD,
    )
    measurement_unit = CharField(
        verbose_name='Единицы измерения',
        max_length=MAX_LEN_RECIPES_CHARFIELD,
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)
        constraints = (
            UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_for_ingredient'
            ),
            CheckConstraint(
                check=Q(name__length__gt=0),
                name='\n%(app_label)s_%(class)s_name is empty\n',
            ),
            CheckConstraint(
                check=Q(measurement_unit__length__gt=0),
                name='\n%(app_label)s_%(class)s_measurement_unit is empty\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.name} {self.measurement_unit}'


class Recipe(Model):
    """Модель для рецептов.

    Основная модель приложения описывающая рецепты.

    Attributes:
        name(str):
            Название рецепта. Установлены ограничения по длине.
        author(int):
            Автор рецепта. Связан с моделю User через ForeignKey.
        tags(int):
            Связь M2M с моделью Tag.
        ingredients(int):
            Связь M2M с моделью Ingredient. Связь создаётся посредством модели
            AmountIngredient с указанием количества ингридиента.
        pub_date(datetime):
            Дата добавления рецепта. Прописывается автоматически.
        image(str):
            Изображение рецепта. Указывает путь к изображению.
        text(str):
            Описание рецепта. Установлены ограничения по длине.
        cooking_time(int):
            Время приготовления рецепта.
            Установлены ограничения по максимальным и минимальным значениям.
    """
    name = CharField(
        verbose_name='Название блюда',
        max_length=MAX_LEN_RECIPES_CHARFIELD,
    )
    author = ForeignKey(
        verbose_name='Автор рецепта',
        related_name='recipes',
        to=User,
        on_delete=CASCADE,
    )
    tags = ManyToManyField(
        verbose_name='Тег',
        related_name='recipes',
        to='Tag',
    )
    ingredients = ManyToManyField(
        verbose_name='Ингредиенты блюда',
        related_name='recipes',
        to=Ingredient,
        through='recipes.AmountIngredient',
    )
    pub_date = DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    image = ImageField(
        verbose_name='Изображение блюда',
        upload_to='recipe_images/',
    )
    text = TextField(
        verbose_name='Описание блюда',
        max_length=MAX_LEN_RECIPES_TEXTFIELD,
    )
    cooking_time = PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        default=MIN_VALUE_COOKING,
        validators=(
            MinValueValidator(
                MIN_VALUE_COOKING,
                'Ваше блюдо уже готово!'
            ),
            MaxValueValidator(
                MAX_VALUE_COOKING,
                'Очень долго ждать...'
            ),
        ),
    )

    def copy(self):
        self.id = None
        self.save()

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        constraints = (
            UniqueConstraint(
                fields=('name', 'author'),
                name='unique_for_author'
            ),
            CheckConstraint(
                check=Q(name__length__gt=0),
                name='\n%(app_label)s_%(class)s_name is empty\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.name}. Автор: {self.author.username}'


class AmountIngredient(Model):
    """Количество ингридиентов в блюде.

    Модель связывает Recipe и Ingredient с указанием количества ингридиента.

    Attributes:
        recipe(int):
            Связаный рецепт. Связь через ForeignKey.
        ingredient(int):
            Связаный ингридиент. Связь через ForeignKey.
        amount(int):
            Количиства ингридиента в рецепте. Установлены ограничения
            по минимальному и максимальному значениям.
    """
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        verbose_name='В каких рецептах',
        related_name='amount_ingredients',
    )
    ingredients = ForeignKey(
        Ingredient,
        on_delete=CASCADE,
        verbose_name='Связанные ингредиенты',
        related_name='amount_ingredients',
    )
    amount = PositiveSmallIntegerField(
        verbose_name='Количество',
        default=MIN_AMOUNT_INGREDIENT,
        validators=(
            MinValueValidator(
                MIN_AMOUNT_INGREDIENT, 'Нужно хоть какое-то количество.'
            ),
            MaxValueValidator(
                MAX_AMOUNT_INGREDIENT, 'Слишком много!'
            ),
        ),
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Количество ингридиентов'
        ordering = ('recipe',)
        constraints = (
            UniqueConstraint(
                fields=('recipe', 'ingredients',),
                name='\n%(app_label)s_%(class)s ingredient alredy added\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.amount} {self.ingredients}'


class Favorite(Model):
    """Модель для списка избранного.

    Модель приложения, формирующая списки избранного.
    """
    user = ForeignKey(
        verbose_name='Владелец списка избранного',
        related_name='favorites',
        to=User,
        on_delete=CASCADE,
    )

    recipe = ManyToManyField(
        verbose_name='Список избранных рецептов',
        related_name='favorites',
        to=Recipe,
    )

    class Meta:
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Списки избранного'
        ordering = ('-id',)
        constraints = [
            UniqueConstraint(
                fields=('user',),
                name='recipes_favorites_unique',
            )
        ]

    def __str__(self) -> str:
        return f'{self.user} {self.recipe}'


class OrderCart(Model):
    """Модель для списка покупок.

    Модель приложения, формирующая корзину.
    """
    user = ForeignKey(
        verbose_name='Автор рецепта',
        related_name='shoppingcart',
        to=User,
        on_delete=CASCADE,
    )

    recipe = ManyToManyField(
        verbose_name='Список покупок',
        related_name='shoppingcart',
        to=Recipe,
    )

    class Meta:
        default_related_name = 'shoppingcart'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Списки корзин'
        ordering = ('-id',)
        constraints = [
            UniqueConstraint(
                fields=('user',),
                name='recipes_shoppingcart_unique',
            )
        ]

    def __str__(self) -> str:
        return f'{self.user} {self.recipe}'
