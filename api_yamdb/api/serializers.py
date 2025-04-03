import secrets

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import APIException, status
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.settings import DEFAULT_FROM_EMAIL
from reviews.models import (
    Category, Comment, Genre, RATING_VALUES, Review, Title)


User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category.

    Используется для работы с данными категорий.
    """
    class Meta:
        model = Category
        exclude = ['id',]


class GenreSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Genre.

    Используется для работы с данными жанров.
    """
    class Meta:
        model = Genre
        exclude = ['id',]


class TitleReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения данных произведения (Title).

    Используется для получения информации о произведении.
    """
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Title
        fields = '__all__'


class TitleWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для записи данных произведения (Title).

    Используется для создания и обновления информации о произведении.
    """
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'

    def validate(self, attrs):
        """
        Проверяет корректность данных перед сохранением.

        Проверяет наличие категории и жанра, если они предоставлены.
        """
        if 'category' in attrs and not attrs.get('category'):
            raise ValidationError('Необходимо указать категорию.')
        if 'genre' in attrs and not attrs.get('genre'):
            raise ValidationError('Необходимо указать хотя бы 1 жанр.')
        return attrs


class SignUpSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания нового пользователя
    и отправки кода подтверждения.
    """

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate_username(self, value):
        """
        Метод проверяющий поле "username" на соответствие условию
        создания юзернеймов.
        """
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Использование имени "me" под запретом.')
        return value

    def validate(self, data):
        """
        Метод валидирующий входные данные.

        Проверка наличия "email" и "username" в базе данных.
        """
        email = data.get('email')
        username = data.get('username')
        email_exists = User.objects.filter(email=email).exists()
        username_exists = User.objects.filter(username=username).exists()
        if email_exists:
            user = User.objects.get(email=email)
            if user.username != username:
                raise ValidationError(
                    'Такой email уже используется другим пользователем.')
        elif username_exists:
            raise ValidationError(
                'Пользователь с таким username уже существует.')
        return data

    def create(self, validated_data):
        """
        Создание пользователя и кода подтверждения.
        """
        email = validated_data['email']
        username = validated_data['username']
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': username,
                'confirmation_code': secrets.token_urlsafe(16)
            }
        )
        if not created:
            user.confirmation_code = secrets.token_urlsafe(16)
            user.save()
        send_mail(
            subject='Код для получения токена',
            message=f'Ваш код: {user.confirmation_code}',
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return user


class TokenObtainSerializer(serializers.Serializer):
    """
    Сериализатор для создания или обновления токена.
    """
    username = serializers.CharField(max_length=150, required=True)
    confirmation_code = serializers.CharField(max_length=100, required=True)

    def validate(self, attrs):
        username = attrs.get('username')
        confirmation_code = attrs.get('confirmation_code')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise APIException(
                detail='Пользователь с таким "username" не существует.',
                code=status.HTTP_404_NOT_FOUND)
        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError(
                'Неверный код подверждения.')
        token = AccessToken.for_user(user)
        return {'token': str(token)}


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
        title = get_object_or_404(
            Title, id=self.context['view'].kwargs.get('title_id'))
        request = self.context['view'].request
        author = request.user
        if request.method == 'POST':
            if Review.objects.filter(author=author, title=title).exists():
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
