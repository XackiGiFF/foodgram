"""Модуль для создания, настройки и управления моделью пользователей.

Задаёт модели и методы для настроийки и управления пользователями
приложения `Foodgram`. Модель пользователя основана на модели
AbstractUser из Django для переопределения полей обязательных для заполнения.
"""
from django.contrib.auth.models import AbstractUser
from django.db.models import (CASCADE, CharField, CheckConstraint, EmailField,
                              F, ForeignKey, ManyToManyField, Model, Q,
                              UniqueConstraint)
from django.db.models.functions import Length

from users.manager.conf import (EMAIL_HELP, FIRST_NAME_HELP, LAST_NAME_HELP,
                                MAX_LEN_EMAIL_FIELD, MAX_LEN_USERS_CHARFIELD,
                                MIN_USERNAME_LENGTH, USER_NAME_HELP)
from users.validators import MinLenValidator, OneOfTwoValidator

CharField.register_lookup(Length)


class User(AbstractUser):
    """Настроенная под приложение `Foodgram` модель пользователя.

    При создании пользователя все поля обязательны для заполнения.

    Attributes:
        email(str):
            Адрес email пользователя.
            Проверка формата производится внутри Dlango.
            Установлено ограничение по максимальной длине.
        username(str):
            Юзернейм пользователя.
            Установлены ограничения по минимальной и максимальной длине.
            Для ввода разрешены только буквы.
        first_name(str):
            Реальное имя пользователя.
            Установлено ограничение по максимальной длине.
        last_name(str):
            Реальная фамилия пользователя.
            Установлено ограничение по максимальной длине.
        password(str):
            Пароль для авторизации.
            Внутри Django проходит хэш-функцию с добавлением
            `соли` settings.SECRET_KEY.
            Хранится в зашифрованном виде.
            Установлено ограничение по максимальной длине.
        subscribe(int):
            Ссылки на id связанных пользователей.
    """
    email = EmailField(
        verbose_name='Адрес электронной почты',
        max_length=MAX_LEN_EMAIL_FIELD,
        unique=True,
        help_text=EMAIL_HELP
    )
    username = CharField(
        verbose_name='Уникальный юзернейм',
        max_length=MAX_LEN_USERS_CHARFIELD,
        unique=True,
        help_text=USER_NAME_HELP,
        validators=(
            MinLenValidator(min_len=MIN_USERNAME_LENGTH),
            OneOfTwoValidator(),
        ),
    )
    first_name = CharField(
        verbose_name='Имя',
        max_length=MAX_LEN_USERS_CHARFIELD,
        help_text=FIRST_NAME_HELP
    )
    last_name = CharField(
        verbose_name='Фамилия',
        max_length=MAX_LEN_USERS_CHARFIELD,
        help_text=LAST_NAME_HELP
    )
    subscribe = ManyToManyField(
        verbose_name='Подписка',
        related_name='subscribers',
        to='Subscribe',
        symmetrical=False,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username', 'first_name', 'last_name')
        constraints = (
            CheckConstraint(
                check=Q(username__length__gte=MIN_USERNAME_LENGTH),
                name='\nusername too short\n',
            ),
        )

    def __str__(self):
        return f'{self.username}: {self.email}'


class Subscribe(Model):
    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='author',
        verbose_name='Автор'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Подписка на авторов'
        verbose_name_plural = 'Подписки на авторов'
        constraints = [
            CheckConstraint(
                check=~Q(author=F('user')),
                name='subscribe_prevent_self_subscribe'),
            UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribe'
            )
        ]

    def __str__(self):
        return f'{self.user.username} {self.author.username}'
