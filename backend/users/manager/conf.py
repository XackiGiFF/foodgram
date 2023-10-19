"""
Модуль настроек users `Food gram`.
"""

"""
Ограничители
"""

# Минимальная длина Username
MIN_USERNAME_LENGTH = 3

# Максимальное количество символов в Username
MAX_LEN_USERS_CHARFIELD = 150

# Максимальное количество символов в Email
MAX_LEN_EMAIL_FIELD = 254

"""
Вывод сообщений
"""
USER_NAME_HELP = (
    'Обязательно для заполнения. '
    f'От {MIN_USERNAME_LENGTH} до {MAX_LEN_USERS_CHARFIELD} букв.'
)

FIRST_NAME_HELP = (
    'Имя обязательно для заполнения.'
    f'Максимум {MAX_LEN_USERS_CHARFIELD} букв.'
)

LAST_NAME_HELP = (
    'Фамилия обязательна для заполнения.'
    f'Максимум {MAX_LEN_USERS_CHARFIELD} букв.'
)

EMAIL_HELP = (
    'Обязательно для заполнения. '
    f'Максимум {MAX_LEN_EMAIL_FIELD} букв.'
)
