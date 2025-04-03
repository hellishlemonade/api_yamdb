from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response

from reviews.models import Category, Comment, Genre, Review, Title
from .filters import TitleFilter
from .mixins import BaseModelMixin, CreateUserModelMixin
from .permissions import (
    ContentManagePermission, IsAdminOrReadOnly, IsAdminPermission)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    TokenObtainSerializer,
    UserSerializer
)

User = get_user_model()


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
    permission_classes = [IsAdminOrReadOnly,]
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


class GenreViewSet(BaseModelMixin):
    """
    ViewSet для модели Genre.

    Предоставляет операции создания, просмотра списка и удаления для жанров.
    Не поддерживает операции обновления и детального просмотра
    отдельных объектов.
    Разрешает чтение всем пользователям,
    создание и удаление только администраторам.

    queryset:
        queryset объектов Genre, включающий все жанры.

    serializer_class:
        GenreSerializer - сериализатор для преобразования данных жанров.

    permission_classes:
        Права доступа определены классом IsAdminOrReadOnly.
        Разрешает чтение всем, создание и удаление только администраторам.

    filter_backends:
        Используется SearchFilter для фильтрации списка жанров по полю 'name'.

    search_fields:
        Поле, по которому осуществляется поиск: 'name'.

    lookup_field:
        Поле, используемое для поиска жанра в URL : 'slug'.

    Действия, предоставляемые ViewSet'ом (унаследованы от BaseModelMixin):
    - create (POST): Создание нового жанра.
    - list (GET): Получение списка жанров с возможностью фильтрации по имени.
    - destroy (DELETE): Удаление жанра по слагу (lookup_field = 'slug').
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly,]
    filter_backends = [SearchFilter,]
    search_fields = ['name',]
    lookup_field = 'slug'


class CategoryViewSet(BaseModelMixin):
    """
    ViewSet для модели Category.

    Предоставляет операции создания, просмотра списка и удаления для категорий.
    Не поддерживает операции обновления и детального просмотра
    отдельных объектов.
    Разрешает чтение всем пользователям,
    создание и удаление только администраторам.

    queryset:
        queryset объектов Category, включающий все категории.

    serializer_class:
        CategorySerializer - сериализатор для преобразования данных категорий.

    permission_classes:
        Права доступа определены классом IsAdminOrReadOnly.
        Разрешает чтение всем, создание и удаление только администраторам.

    filter_backends:
        Используется SearchFilter для фильтрации списка категорий
        по полю 'name'.

    search_fields:
        Поле, по которому осуществляется поиск: 'name'.

    lookup_field:
        Поле, используемое для поиска категории в URL : 'slug'.

    Действия, предоставляемые ViewSet'ом (унаследованы от BaseModelMixin):
    - create (POST): Создание новой категории.
    - list (GET): Получение списка категорий с возможностью фильтрации
                  по имени.
    - destroy (DELETE): Удаление категории по слагу (lookup_field = 'slug').
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly,]
    filter_backends = [SearchFilter,]
    search_fields = ['name',]
    lookup_field = 'slug'


class SignUpViewSet(CreateUserModelMixin):
    """
    ViewSet для модели CustomUser.

    Наследуясь от CreateUserModelMixin позволяет создавать пользователей
    и коды подтверждения с помощью сериализатора.
    """
    queryset = User.objects.all()
    serializer_class = SignUpSerializer


class TokenViewSet(CreateUserModelMixin):
    """
    ViewSet для модели CustomUser.

    Наследуясь от CreateUserModelMixin позволяет создавать токены для
    пользователей с помощью сериализатора.
    """
    queryset = User.objects.all()
    serializer_class = TokenObtainSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Review.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = ContentManagePermission

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs['title_id'])

    def get_queryset(self):
        return Review.objects.filter(title=self.get_title())

    def perform_create(self, serializer):
        serializer.save(
            title=self.get_title(),
            author=self.request.user
        )


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Comment.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = ContentManagePermission

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs['review_id'])

    def get_queryset(self):
        return Comment.objects.filter(review=self.get_review())

    def perform_create(self, serializer):
        serializer.save(
            review=self.get_review(),
            author=self.request.user
        )


class UserAdminViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminPermission]
    lookup_field = 'username'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, 
            data=request.data, 
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Эндпоинт для получения текущего пользователя"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
