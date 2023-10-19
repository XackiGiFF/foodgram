from django.db.models import PositiveSmallIntegerField
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework.fields import IntegerField, ReadOnlyField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import (ModelSerializer, SerializerMethodField,
                                        ValidationError)

from .manager.conf import (MAX_LEN_USERS_CHARFIELD, MAX_VALUE_COOKING,
                           MIN_AMOUNT_INGREDIENT, MIN_USERNAME_LENGTH,
                           MIN_VALUE_COOKING, RECIPES_LIMIT)
from recipes.models import (AmountIngredient, Favorite, Ingredient, OrderCart,
                            Recipe, Tag)
from users.models import User, Subscribe
from .validators import search_duplications


class ShortRecipeSerializer(ModelSerializer):
    """Сериализатор для модели Recipe.
    Определён укороченный набор полей для некоторых эндпоинтов.
    """

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time',
        )
        read_only_fields = (
            'id', 'name', 'image', 'cooking_time',
        )


class UserSerializer(ModelSerializer):
    """Сериализатор для использования с моделью User.
    """
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """Проверка подписки пользователей.

        Определяет - подписан ли текущий пользователь
        на просматриваемого пользователя.

        Args:
            obj (User): Пользователь, на которого проверяется подписка.

        Returns:
            bool: True, если подписка есть. Во всех остальных случаях False.
        """
        request = self.context.get('request')

        return (
                request.user.is_authenticated
                and request.user.subscribe.filter(author_id=obj.id).exists()
        )

    def validate_username(self, username):
        """Проверяет введённый юзернейм.

        Args:
            username (str): Введённый пользователем юзернейм.

        Raises:
            ValidationError: Некорректная длина юзернейма.
            ValidationError: Юзернейм содержит не только буквы.

        Returns:
            str: Юзернейм.
        """
        if len(username) < MIN_USERNAME_LENGTH:
            raise ValidationError(
                'Длина username допустима от '
                f'{MIN_USERNAME_LENGTH} до {MAX_LEN_USERS_CHARFIELD}'
            )
        if not username.isalpha():
            raise ValidationError(
                'В username допустимы только буквы.'
            )
        return username.capitalize()


class CheckSubscribeSerializer(ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ('user', 'author')

    def validate(self, data):
        user = data['user']
        author = data['author']
        subscribed = Subscribe.objects.filter(
            user=user, author=author
        ).exists()

        if self.context.get('request').method == 'POST':
            if user == author:
                raise ValidationError(
                    'Вы не можете подписаться на самого себя нельзя'
                )
            if subscribed:
                raise ValidationError(
                    'Вы уже подписаны на этого автора'
                )

        if self.context.get('request').method == 'DELETE':
            if user == author:
                raise ValidationError(
                    'Отписаться от самого себя невозможно!'
                )
            if not subscribed:
                raise ValidationError(
                    'Вы уже отписались от этого автора'
                )
        return data


class UserSubscribeSerializer(UserSerializer):
    """Сериализатор для сохранения авторов на которых подписан текущий пользователь.
    """

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields
        read_only_fields = UserSerializer.Meta.fields

    def validate(self, data):
        request = self.context.get('request')
        author = self.initial_data.get('author')

        subscribed = request.user.subscribe.filter(author_id=author).exists()

        if request.method == 'POST':
            if request.user == author:
                raise ValidationError(
                    'Подписаться на самого себя нельзя'
                )
            if subscribed:
                raise ValidationError(
                    'Вы уже подписаны'
                )
        return data

    def remove(self, validated_data):
        """Удаление рецепта из списка

        Args:
            validated_data (Dict):
                'user': (User): Переданный объект пользователя
                'recipe': (Recipe): Переданный объект рецепта
        """
        user = validated_data.pop('user')
        author = validated_data.pop('author')

        user.subscribe.filter(user=user.id, author=author.id).delete()


class UserSubscribeViewSerializer(UserSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSubscribeSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )
        read_only_fields = UserSubscribeSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')

        queryset = Recipe.objects.filter(author_id=obj.author.id)
        if recipes_limit:
            try:
                # Recipe.objects.filter(author_id=obj.author.id)
                queryset = queryset[:int(recipes_limit)]
            except ValueError:
                queryset = queryset[:int(RECIPES_LIMIT)]
        return ShortRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        """ Показывает общее количество рецептов у каждого автора.

        Args:
            obj (User): Запрошенный пользователь.

        Returns:
            int: Количество рецептов созданных запрошенным пользователем.
        """
        return Recipe.objects.filter(author=obj.id).count()


class TagSerializer(ModelSerializer):
    """Сериализатор для вывода тегов.
    """

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = '__all__',


class IngredientSerializer(ModelSerializer):
    """Сериализатор для вывода ингридиентов.
    """

    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = '__all__',


class IngredientToRecipeSerializer(ModelSerializer):
    """Сериализатор для вывода ингридиентов.
    """
    id = IntegerField(source='ingredients.id')
    name = ReadOnlyField(source='ingredients.name')
    measurement_unit = ReadOnlyField(source='ingredients.measurement_unit')

    class Meta:
        model = AmountIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = '__all__',


class RecipeSerializer(ModelSerializer):
    """ Cериализатор для создания/редактирования рецептов.
    """
    tags = PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    author = UserSerializer(
        read_only=True
    )
    ingredients = IngredientToRecipeSerializer(read_only=True,
                                               many=True)
    cooking_time = PositiveSmallIntegerField(
        validators=[MIN_VALUE_COOKING, MAX_VALUE_COOKING]
    )

    image = Base64ImageField()

    def recipe_amount_ingredients_set(self, recipe, ingredients):
        """Записывает ингредиенты вложенные в рецепт.

        Создаёт объект AmountIngredient связывающий объекты Recipe и
        Ingredient с указанием количества(`amount`) конкретного ингридиента.

        Args:
            recipe (Recipe):
                Рецепт, в который нужно добавить игридиенты.
            Ingredients (list):
                Список ингредиентов и количества сих.
                :param recipe:
                :param ingredients:
        """
        AmountIngredient.objects.bulk_create(
            [AmountIngredient(
                recipe=recipe,
                ingredients=get_object_or_404(Ingredient, id=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def check_amount(self, amount):
        try:
            if int(amount) < MIN_AMOUNT_INGREDIENT:
                raise ValidationError(
                    'Число должно быть положительным'
                )
            else:
                return int(amount)
        except ValueError:
            raise ValidationError(
                'Поле должно быть только числом!'
            )

    def check_time(self, time):
        try:
            if int(time) < MIN_VALUE_COOKING:
                raise ValidationError(
                    'Время: Число должно быть положительным!'
                )
            else:
                return int(time)
        except ValueError:
            raise ValidationError(
                'Время: Поле должно быть только числом!'
            )

    def validate(self, data):
        """Проверка вводных данных при создании/редактировании рецепта.

        Args:
            data (dict): Вводные данные.

        Raises:
            ValidationError: Тип данных несоответствует ожидаемому.

        Returns:
            dict: Проверенные данные.
        """
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')

        self.check_time(data['cooking_time'])

        if not tags:
            raise ValidationError(
                'tags: Отсутствует какой-либо тег!'
            )

        if not ingredients:
            raise ValidationError(
                'ingredients: Отсутствует какой-либо ингридиент!'
            )

        for value in (tags, ingredients):
            if not isinstance(value, list):
                raise ValidationError(
                    f'"{value}" должен быть в формате "[]"'
                )

        valid_ingredients = []

        for ing in ingredients:
            ing_id = ing.get('id')

            self.check_amount(ing.get('amount'))
            if search_duplications(valid_ingredients,
                                   'id', ing_id):
                raise ValidationError(
                    'Поля не должны повторяться!'
                )

            valid_ingredients.append(ing)

        data['ingredients'] = valid_ingredients
        return data

    def create(self, validated_data):
        """Создаёт рецепт.

        Args:
            validated_data (dict): Данные для создания рецепта.

        Returns:
            Recipe: Созданный рецепт.
        """
        image = validated_data.pop('image')
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)
        self.recipe_amount_ingredients_set(recipe, ingredients)
        return recipe

    def update(self, recipe, validated_data):
        """Обновляет рецепт.

        Args:
            recipe (Recipe): Рецепт для изменения.
            validated_data (dict): Изменённые данные.

        Returns:
            Recipe: Обновлённый рецепт.
        """
        tags = validated_data.get('tags')
        ingredients = validated_data.get('ingredients')

        recipe.tags.clear()
        recipe.tags.set(tags)
        recipe.ingredients.clear()

        self.recipe_amount_ingredients_set(recipe, ingredients)

        recipe.save()

        validated_data['ingredients'] = [item['id'] for item in ingredients]

        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context={
            'request': self.context.get('request')
        }).data

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class RecipeReadSerializer(ModelSerializer):
    tags = TagSerializer(
        read_only=True,
        many=True
    )
    author = UserSerializer(
        read_only=True
    )
    ingredients = IngredientToRecipeSerializer(
        many=True,
        read_only=True,
        source='amount_ingredients'
    )
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    is_favorited = SerializerMethodField()

    def get_is_favorited(self, obj):
        """Проверка - находится ли рецепт в избранном.

        Args:
            obj (Recipe): Переданный для проверки рецепт.

        Returns:
            bool: True - если рецепт в `избранном`
            у запращивающего пользователя, иначе - False.
        """
        user = self.context.get('request').user
        return (
                user.is_authenticated
                and user.favorites.filter(user=user.id, recipe=obj.pk).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """Проверка - находится ли рецепт в списке  покупок.

        Args:
            obj (Recipe): Переданный для проверки рецепт.

        Returns:
            bool: True - если рецепт в `списке покупок`
            у запращивающего пользователя, иначе - False.
        """
        user = self.context.get('request').user

        return (
                user.is_authenticated
                and user.shoppingcart.filter(user=user.id, recipe=obj.pk).exists()
        )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'is_favorited',
            'ingredients',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'is_in_shopping_cart_cart',
            'is_favorited',
        )


class FavoriteViewSerializer(ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__',
        read_only_fields = '__all__',


class OrderCartViewSerializer(ModelSerializer):
    class Meta:
        model = OrderCart
        fields = '__all__',
        read_only_fields = '__all__',


class FavoriteSerializer(ModelSerializer):
    recipes = Recipe.objects.all()
    favorites = Favorite.objects.all()
    user = UserSerializer(
        read_only=True
    )
    recipe = ShortRecipeSerializer(
        read_only=True
    )

    def validate(self, data):
        user = self.initial_data.pop('user')
        recipe = self.initial_data.get('recipe')

        if not user.favorites.filter(user=user).exists():
            self.favorites.create(user=user)

        data['user'] = user
        data['recipe'] = recipe

        return data

    def save(self, validated_data):
        """Добавление рецепта в список

        Args:
            validated_data (Dict):
                'user': (User): Переданный объект пользователя
                'recipe': (Recipe): Переданный объект рецепта
        """
        user = validated_data.pop('user')
        recipe = validated_data.pop('recipe')

        if user.favorites.filter(recipe=recipe).exists():
            raise ValidationError(
                'Рецепт уже был добавлен в избранное'
            )

        favorite = self.favorites.get(user=user)

        favorite.recipe.add(recipe)

    def remove(self, validated_data):
        """Удаление рецепта из списка

        Args:
            validated_data (Dict):
                'user': (User): Переданный объект пользователя
                'recipe': (Recipe): Переданный объект рецепта
        """
        user = validated_data.pop('user')
        recipe = validated_data.pop('recipe')

        favorite = self.favorites.get(user=user)

        favorite.recipe.remove(recipe)

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')


class OrderCartSerializer(ModelSerializer):
    recipes = Recipe.objects.all()
    shoppingcart = OrderCart.objects.all()
    user = UserSerializer(
        read_only=True
    )
    recipe = ShortRecipeSerializer(
        read_only=True
    )

    def validate(self, data):
        user = self.initial_data.pop('user')
        recipe = self.initial_data.get('recipe')

        if not user.shoppingcart.filter(user=user).exists():
            self.shoppingcart.create(user=user)

        data['user'] = user
        data['recipe'] = recipe

        return data

    def save(self, validated_data):
        """Добавление рецепта в список

        Args:
            validated_data (Dict):
                'user': (User): Переданный объект пользователя
                'recipe': (Recipe): Переданный объект рецепта
        """
        user = validated_data.pop('user')
        recipe = validated_data.pop('recipe')

        if user.shoppingcart.filter(recipe=recipe).exists():
            # self.remove(data)
            raise ValidationError(
                'Рецепт уже был добавлен в список покупок'
            )

        shoppingcart = self.shoppingcart.get(user=user)

        shoppingcart.recipe.add(recipe)

    def remove(self, validated_data):
        """Удаление рецепта из списка

        Args:
            validated_data (Dict):
                'user': (User): Переданный объект пользователя
                'recipe': (Recipe): Переданный объект рецепта
        """
        user = validated_data.pop('user')
        recipe = validated_data.pop('recipe')

        shoppingcart = self.shoppingcart.get(user=user)

        shoppingcart.recipe.remove(recipe)

    class Meta:
        model = OrderCart
        fields = ('user', 'recipe')
