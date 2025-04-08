from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import (
    NotFound, ValidationError)
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.settings import DEFAULT_FROM_EMAIL
from reviews.models import Category, Comment, Genre, Review, Title
from .filters import TitleFilter
from .mixins import CreateListDestroyModelMixin
from .permissions import (
    ContentManagePermission,
    IsAdminOrReadOnly,
    IsAdminPermission,
    IsUserPermissions
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    TokenObtainSerializer,
    UserSerializer,
    MeSerializer
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
                .annotate(rating=Avg('reviews__score'))
                .all()
                )
    http_method_names = ['get', 'post', 'patch', 'delete', ]
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = [DjangoFilterBackend, ]
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


class GenreViewSet(CreateListDestroyModelMixin):
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

    Действия, предоставляемые ViewSet'ом (унаследованы от
    CreateListDestroyModelMixin):
    - create (POST): Создание нового жанра.
    - list (GET): Получение списка жанров с возможностью фильтрации по имени.
    - destroy (DELETE): Удаление жанра по слагу (lookup_field = 'slug').
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = [SearchFilter, ]
    search_fields = ['name', ]
    lookup_field = 'slug'


class CategoryViewSet(CreateListDestroyModelMixin):
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
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = [SearchFilter, ]
    search_fields = ['name', ]
    lookup_field = 'slug'


@api_view(['POST'])
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user, _ = User.objects.get_or_create(
        username=request.data['username'], email=request.data['email']
    )
    token = default_token_generator.make_token(user)
    send_mail(
        subject='Код для получения токена',
        message=f'Ваш код: {token}',
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return Response(data=serializer.data)


@api_view(['POST'])
def token(request):
    serializer = TokenObtainSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(username=request.data['username'])
    if not default_token_generator.check_token(
        user, request.data['confirmation_code']
    ):
        raise ValidationError(
            {'confirmation_code': 'Неверный код подтверждения.'})
    token = AccessToken.for_user(user)
    return Response({'token': str(token)})


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Review.
    """
    serializer_class = ReviewSerializer
    permission_classes = (ContentManagePermission,)
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']

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
    serializer_class = CommentSerializer
    permission_classes = (ContentManagePermission,)
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs['review_id'])
        # Для получения объекта отзыва надо в get_object_or_404 также использовать title_id из запроса, чтобы проверить, корректность запроса.

    def get_queryset(self):
        return Comment.objects.filter(review=self.get_review())

    def get_object(self):
        # Лишний метод.
        review_id = self.kwargs['review_id']
        if (
            not Review.objects.filter(
                id=review_id,
                title__id=self.kwargs['title_id']
            ).exists()
            or not Comment.objects.filter(
                id=self.kwargs['pk'],
                review__id=review_id
            ).exists()
        ):
            raise NotFound()
        return super().get_object()

    def perform_create(self, serializer):
        serializer.save(
            review=self.get_review(),
            author=self.request.user
        )


class UserAdminViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели CustomUser.

    Предоставляет операции CRUD за исключением PUT-запросов.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminPermission,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action == 'me':
            return MeSerializer
        return UserSerializer

    @action(
        detail=False,
        methods=('get', 'patch'),
        permission_classes=(IsUserPermissions,)
    )
    def me(self, request):
        """Эндпоинт /me/ с отдельным сериализатором"""
        user = request.user
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        serializer = self.get_serializer(user)
        return Response(serializer.data)
