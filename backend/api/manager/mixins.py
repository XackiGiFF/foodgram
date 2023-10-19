"""Модуль содержит дополнительные классы
для настройки основных классов приложения.
"""
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)

from .conf import (ADD_METHODS, DEL_METHODS, FAVORITE_M2M, SHOP_CART_M2M,
                   SUBSCRIBE_M2M)


class AddDelViewMixin:
    """
    Добавляет во Viewlet дополнительные методы.

    Содержит метод добавляющий/удаляющий объект связи
    Many-to-Many между моделями.
    Требует определения атрибута `add_serializer`.

    Example:
        class ExampleViewSet(ModelViewSet, AddDelViewMixin)
            ...
            add_serializer = ExampleSerializer

            def example_func(self, request, **kwargs):
                ...
                obj_id = ...
                return self.add_del_obj(obj_id, manager.M2M)
    """

    add_serializer = None

    def __init__(self):
        self.queryset = None
        self.request = None

    def add_del_obj(self, request, id, model, data, serializer):
        """Добавляет/удаляет связь через менеджер `model.many-to-many`.

        Args:
            model:
            result:
            data: Передаваемые параметры
            request (Request):
                Запрос содержащий данные сессии.
            serializer (Serializer):
                Cодержит cериализатор для валидации и работы
                с выбранным объектом

        Returns:
            Response: Статус подтверждающий/отклоняющий действие.
        """

        models = {
            SUBSCRIBE_M2M: request.user.subscribe,
            FAVORITE_M2M: request.user.favorites,
            SHOP_CART_M2M: request.user.shoppingcart,
        }
        model = models[model]

        obj = get_object_or_404(self.queryset, id=id)

        if request.method in ADD_METHODS:
            serializer.is_valid(raise_exception=True)

            serializer = self.add_serializer(
                obj,
                data=data,
                context={'request': self.request})
            validated_data = serializer.is_valid()

            if model == SUBSCRIBE_M2M:
                result = model.create(user=validated_data['user'], author_id=obj.id)
                serializer = self.add_serializer(
                    result, context={'request': request}
                )
            return Response(serializer.data, status=HTTP_201_CREATED)

        if request.method in DEL_METHODS:
            serializer.is_valid(raise_exception=True)

            serializer = self.add_serializer(
                obj,
                data=data,
                context={'request': self.request})
            serializer.is_valid()
            model.filter(author=obj).delete()
            return Response(serializer.data,
                            status=HTTP_204_NO_CONTENT)

        return Response({'error': 'Ошибка, не найдено!'},
                        status=HTTP_400_BAD_REQUEST)
