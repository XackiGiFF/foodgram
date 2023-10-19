"""
Модуль настроек API `Food gram`.
"""

DATE_TIME_FORMAT = '%d/%m/%Y %H:%M'

ADD_METHODS = ('GET', 'POST',)

DEL_METHODS = ('DELETE',)

ACTION_METHODS = [s.lower() for s in (ADD_METHODS + DEL_METHODS)]

UPDATE_METHODS = ('PUT', 'PATCH')

SYMBOL_TRUE_SEARCH = ('1', 'true',)

SYMBOL_FALSE_SEARCH = ('0', 'false',)

# Создание "подписки". <user.subscribe>
SUBSCRIBE_M2M = 'subscribe'
# Добавление рецепта в "избранное". <user.favorites>
FAVORITE_M2M = 'favorite'
# Добавление рецепта в "список покупок". <user.carts>
SHOP_CART_M2M = 'shoppingcart'

"""
Ограничители (Необходимо для добавления пользователей)
"""

# Минимальная длина Username
MIN_USERNAME_LENGTH = 3

# Максимальное количество символов в Username
MAX_LEN_USERS_CHARFIELD = 150

# Минимальное время приготовления
MIN_VALUE_COOKING = 1

# Максимальное время приготовления
MAX_VALUE_COOKING = 600

# Минимальное количество ингредиента
MIN_AMOUNT_INGREDIENT = 1

# Максимальное время приготовления
MAX_AMOUNT_INGREDIENT = 10000

# Формат цвета #RGB
MIN_COLOR_LEN = 3

# Формат цвета #0064FF
MAX_COLOR_LEN = 6

# Количество карточек на странице
PAGE_SIZE_COUNT = 6

# Лимит рецептов
RECIPES_LIMIT = 3
