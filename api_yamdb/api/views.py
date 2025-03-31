from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from reviews.models import Title
from .filters import TitleFilter
from .serializers import TitleReadSerializer, TitleWriteSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Title.

    Предоставляет CRUD операции для произведений (Titles).
    Разрешает чтение всем пользователям, создание, обновление и удаление
    только администраторам.

    queryset:
        queryset объектов Title, включающий все произведения.
        В будущем планируется добавление аннотации 'rating' для
        вычисления среднего рейтинга на основе отзывов.

    permission_classes:
        Права доступа определены классом IsAdminOrReadOnly.
        Разрешает чтение всем, запись, обновление и удаление только
        администраторам.

    filter_backends:
        Используется DjangoFilterBackend для фильтрации списка произведений.

    filterset_class:
        Для фильтрации используется TitleFilter, предоставляющий
        возможность фильтрации произведений по различным полям,
        определенным в TitleFilter (например, по категории, жанру, году)."
    """
    queryset = (Title.objects
                # .annotate(rating=Avg('reviews__score'))
                # после добавления модели Review
                # будем добавлять средний рейтинг
                .all())
    permission_classes = [IsAdminOrReadOnly,]  # заглушка
    filter_backends = [DjangoFilterBackend,]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        """
        Определяет, какой сериализатор использовать в зависимости от действия.
        - Для действий 'list' (получение списка) и 'retrieve' (получение
          детальной информации) используется TitleReadSerializer,
          предназначенный для чтения данных.
        - Для остальных действий (create, partial_update, delete) используется
          TitleWriteSerializer, предназначенный для записи данных.
        """
        if self.action in ['list', 'retrieve']:
            return TitleReadSerializer
        return TitleWriteSerializer
