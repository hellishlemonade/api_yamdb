from rest_framework.mixins import (
    CreateModelMixin, ListModelMixin, DestroyModelMixin
)
from rest_framework.viewsets import GenericViewSet


class CreateListDestroyModelMixin(CreateModelMixin, ListModelMixin,
                                  DestroyModelMixin, GenericViewSet):
    """
    Миксин для создания ViewSet'ов, предоставляющих базовые операции CRUD.

    Наследует функциональность для создания новых объектов (CreateModelMixin),
    получения списка объектов (ListModelMixin)
    и удаления объектов (DestroyModelMixin).
    В сочетании с GenericViewSet, предоставляет стандартный набор действий
    для моделей, таких как создание, получение списка и удаление.

    Этот миксин предназначен для использования с ViewSet'ами, которые требуют
    только базовые операции создания, просмотра списка и удаления,
    без необходимости в операциях обновления
    или детального просмотра отдельных объектов.

    Примеры использования:
    - ViewSet для управления жанрами (только создание, список и удаление).
    - ViewSet для управления категориями (только создание, список и удаление).

    Действия, предоставляемые миксином:
    - create (POST): Создание нового объекта.
    - list (GET): Получение списка всех объектов.
    - destroy (DELETE): Удаление объекта по идентификатору (lookup_field).
    """
    pass


class CreateUserModelMixin(CreateModelMixin, GenericViewSet):
    """
    Миксин для создания ViewSet'ов, выполняющих POST запросы.

    Наследует функциональность для создания новых объектов (CreateModelMixin),
    В сочетании с GenericViewSet, предоставляет создвние объекта для модели.

    Примеры использования:
    - ViewSet для создания пользователя.
    - ViewSet для создания токена для польщователя.
    """
    pass
