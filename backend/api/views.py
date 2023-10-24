from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import Favorite, Ingredient, Recipe, Tag
from users.models import User, Subscribe
from .filters import IngredientSearchFilter, RecipeAndCartFilter
from .manager.conf import ACTION_METHODS, ADD_METHODS, DEL_METHODS
from .manager.mixins import AddDelViewMixin
from .manager.order_cart import download_cart
from .paginators import PageLimitPagination
from .permissions import AuthorStaffOrReadOnly
from .serializers import (FavoriteSerializer,
                          FavoriteViewSerializer, IngredientSerializer,
                          OrderCartSerializer, RecipeReadSerializer,
                          RecipeSerializer, ShortRecipeSerializer,
                          TagSerializer, UserSubscribeSerializer)


class UserViewSet(DjoserUserViewSet, AddDelViewMixin):
    """Работает с пользователями.

    ViewSet для работы с пользователями - вывод таковых,
    регистрация.
    Для авторизованных пользователей —
    возможность подписаться на автора рецепта.
    """
    pagination_class = PageLimitPagination
    permission_classes = (AuthorStaffOrReadOnly,)
    add_serializer = UserSubscribeSerializer

    @action(
        methods=ACTION_METHODS,
        detail=True,
    )
    def subscribe(self, request, id):
        """Создаёт/удалит связь между пользователями.

        Вызов метода через url: */user/<int:id>/subscribe/.

        Args:
            request (Request): Не используется.
            id (int, str):
                id пользователя, на которого желает подписаться
                или отписаться запрашивающий пользователь.

        Returns:
            Response: Статус подтверждающий/отклоняющий действие.
        """
        user = request.user
        author = get_object_or_404(User, pk=id)

        serializer = self.add_serializer(
            data={'user': user.id, 'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        if request.method in ADD_METHODS:
            result = Subscribe.objects.create(user=user, author=author)
            serializer = self.add_serializer(
                result, context={'request': request}
            )

            return Response(serializer.data, status=HTTP_201_CREATED)

        if request.method in DEL_METHODS:
            user.subscriber.filter(author=author.id).delete()

            return Response('Подписка успешно удалена',
                            status=HTTP_204_NO_CONTENT)

    @action(
        methods=('get',),
        detail=False,
    )
    def subscriptions(self, request):
        """Список подписок пользоваетеля.

        Вызов метода через url: */user/<int:id>/subscriptions/.

        Args:
            request (Request): Не используется.

        Returns:
            Response:
                401 - для неавторизованного пользователя.
                Список подписок для авторизованного пользователя.
        """
        user = self.request.user
        authors = user.subscriber.all()
        pages = self.paginate_queryset(authors)
        serializer = self.add_serializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    """Работает с тегами.

    Изменение и создание тегов разрешено только админам.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backend = (DjangoFilterBackend,)
    search_fields = ('^tags',)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class FavoriteViewSet(ModelViewSet, AddDelViewMixin):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteViewSerializer

    def favorite(self, request, *args, **kwargs):
        """Добавляет/удалет рецепт в `избранное`.

        Вызов метода через url: */recipe/<int:pk>/favorite/.

        Args:
            request (Request): Запрос содержащий данные сессии.
            args (args):
                Содержит id рецепта, который
                нужно добавить/удалить из `избранного`.

        Returns:
            Response: Статус подтверждающий/отклоняющий действие.
        """
        recipe_id = self.kwargs['id']
        recipe = get_object_or_404(Recipe, id=recipe_id)

        serializer = FavoriteSerializer(
            data={'user': request.user, 'recipe': recipe},
            context={'request': request})
        serializer.is_valid()
        param = {
            'user': request.user,
            'recipe': recipe
        }
        return self.add_del_obj(request, serializer, param)


class RecipeViewSet(ModelViewSet, AddDelViewMixin):
    """Работает с рецептами.

    Вывод, создание, редактирование, добавление/удаление
    в избранное и список покупок.
    Отправка текстового файла со списком покупок.
    Для авторизованных пользователей — возможность добавить
    рецепт в избранное и в список покупок.
    Изменять рецепт может только автор или админы.
    """
    queryset = Recipe.objects.select_related('author')
    permission_classes = (AuthorStaffOrReadOnly,)
    filterset_class = RecipeAndCartFilter
    pagination_class = PageLimitPagination
    add_serializer = ShortRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        return RecipeSerializer

    @action(
        methods=ACTION_METHODS,
        detail=True,
    )
    def shopping_cart(self, request, pk):
        """Добавляет/удалет рецепт в `список покупок`.

        Вызов метода через url: *//recipe/<int:pk>/shopping_cart/.

        Args:
            request (Request): Запрос содержащий данные сессии.
            pk (int, str):
                id рецепта, который нужно добавить/удалить в `корзину покупок`.

        Returns:
            Response: Статус подтверждающий/отклоняющий действие.
        """
        obj = get_object_or_404(self.queryset, id=pk)
        recipe = ShortRecipeSerializer(
            obj,
            context={'request': request},
        ).data

        serializer = OrderCartSerializer(
            obj,
            data={'user': request.user, 'recipe': recipe},
            context={'request': request})
        serializer.is_valid()

        param = {
            'user': request.user,
            'recipe': obj
        }
        return self.add_del_obj(request, serializer, param)

    @action(
        methods=('get',),
        detail=False,
    )
    def download_shopping_cart(self, request):
        """Загружает файл *.txt со списком покупок.

        Считает сумму ингредиентов в рецептах выбранных для покупки.
        Возвращает текстовый файл со списком ингредиентов.
        Вызов метода через url:  */recipe/<int:id>/download_shopping_cart/.

        Args:
            request (Request): Не используется.

        Returns:
            Response: Ответ с текстовым файлом.
        """
        shopping_list = download_cart(self.request.user)

        filename = f'{self.request.user.username}_shopping_list.txt'

        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response
