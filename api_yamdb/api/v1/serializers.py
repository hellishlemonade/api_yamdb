from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from rest_framework.exceptions import NotFound
from rest_framework import serializers

from api_yamdb.settings import MAX_EMAIL_LENGTH
from reviews.models import (
    Category, Comment, Genre, Review, Title)
from users.models import MAX_LENGTH_USERNAME
from users.validators import validate_username


User = get_user_model()


ERROR_USERNAME = 'Пользователь с таким username уже существует.'
ERROR_EMAIL = 'Пользователь с таким email уже существует.'
MAX_LENGTH_CODE = 100
RATING_VALUES = [(i, str(i)) for i in range(1, 11)]


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category.

    Используется для работы с данными категорий.
    """
    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Genre.

    Используется для работы с данными жанров.
    """
    class Meta:
        model = Genre
        exclude = ('id', )


class TitleReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения данных произведения (Title).

    Используется для получения информации о произведении.
    """
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category', 'rating')


class TitleWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для записи данных произведения (Title).

    Используется для создания и обновления информации о произведении.
    """
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        allow_empty=False
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
        allow_null=False,
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category',)

    def to_representation(self, title):
        """Определяет, какой сериализатор будет использоваться для чтения."""

        return TitleReadSerializer(title).data


class SignUpSerializer(serializers.Serializer):
    """
    Сериализатор для создания нового пользователя
    и отправки кода подтверждения.
    """
    username = serializers.CharField(
        max_length=MAX_LENGTH_USERNAME,
        validators=[UnicodeUsernameValidator(), validate_username])
    email = serializers.EmailField(max_length=MAX_EMAIL_LENGTH)

    def validate(self, data):
        """
        Метод валидирующий входные данные.

        Проверка наличия "email" и "username" в базе данных.
        """
        email = data.get('email')
        username = data.get('username')
        email_user = User.objects.filter(email=email).first()
        username_user = User.objects.filter(username=username).first()
        if email_user != username_user:
            error_msg = {}
            if email_user is not None:
                error_msg['email'] = ERROR_EMAIL
            if username_user is not None:
                error_msg['username'] = ERROR_USERNAME
            raise ValidationError(error_msg)
        return data


class TokenObtainSerializer(serializers.Serializer):
    """
    Сериализатор для работы с токеном.
    """
    username = serializers.CharField(
        max_length=MAX_LENGTH_USERNAME,
        validators=[UnicodeUsernameValidator(), validate_username])
    confirmation_code = serializers.CharField(max_length=MAX_LENGTH_CODE)


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для выполнения CRUD операций с моделью CustomUser
    """
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role')


class MeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для выполнения операций получения экземпляра
    и внесения изменений в собственный профиль.
    """
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role')
        read_only_fields = ('role',)


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Review.
    """
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    score = serializers.ChoiceField(choices=RATING_VALUES)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('title',)

    def validate(self, attrs):
        request = self.context['view'].request
        author = request.user
        if request.method == 'POST':
            if Review.objects.filter(
                author=author,
                title__id=self.context['view'].kwargs.get('title_id')
            ).exists():
                raise ValidationError('Такой отзыв уже есть.')
        return super().validate(attrs)


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Comment.
    """
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('review',)

    def validate(self, attrs):
        # Лишнее. Запрос получается во вьюсете.
        if not Review.objects.filter(
            id=self.context['view'].kwargs.get('review_id'),
            title__id=self.context['view'].kwargs.get('title_id')
        ).exists():
            raise NotFound()
        return super().validate(attrs)
