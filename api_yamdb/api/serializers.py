from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import (
    Category, Comment, Genre, RATING_VALUES, Review, Title)
from users.models import MAX_LENGTH_USERNAME
from users.validators import validate_username


MAX_LENGTH_EMAIL = 254

User = get_user_model()


ERROR_USERNAME = 'Пользователь с таким username уже существует.'
ERROR_EMAIL = 'Пользователь с таким email уже существует.'
ERROR_REQUIRED_VALUE = 'Отсутствует обязательное поле.'


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category.

    Используется для работы с данными категорий.
    """
    class Meta:
        model = Category
        exclude = ['id', ] 
        # Когда объявляется коллекция, нужно верно выбрать между списком и кортежем(тут список).
        # Выбор нужно делать осознанно, потому что список изменяемый, а кортеж нет.
        # Если предполагается, что сюда будет вноситься изменения где то в коде, то нужен список, а если изменений никаких не будет то лучше кортеж.
        # Тут и далее по всему коду.


class GenreSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Genre.

    Используется для работы с данными жанров.
    """
    class Meta:
        model = Genre
        exclude = ['id', ]


class TitleReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения данных произведения (Title).

    Используется для получения информации о произведении.
    """
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.SerializerMethodField(read_only=True) 
    # Тут хватит IntegerField,
    # в котором надо будет указать
    # параметр default (дефолтом будет None).

    class Meta:
        model = Title
        fields = '__all__' 
        # Модель может измениться, а с такой настройкой наш АПИ
        # уже не будет соответствовать спецификации.
        # Описываем явно поля.
        # Тут и далее.

    def get_rating(self, obj): 
        # Такой подход породит множество запросов в БД (отдельный запрос для каждого элемента QuerySet).
        # Нужно изменить подход: добавьте атрибут rating для всех элементов QuerySet путем его аннотирования во вью.
        """
        Возвращает средний рейтинг произведения.

        Если произведение не имеет отзывов, возвращает 0.
        """
        annotated_title = Title.objects.annotate(
            rating=Avg('reviews__score')
        ).get(pk=obj.pk)
        return annotated_title.rating or None


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

    def to_representation(self, title):
        """Определяет, какой сериализатор будет использоваться для чтения."""
        serializer = TitleReadSerializer(title) 
        # Одноразовая переменная.
        return serializer.data

    def validate(self, attrs): 
        # Да, нельзя создавать произведение если у жанра указан пустой список.
        # Но метод лишний, смотрим в сторону атрибутов allow_null и allow_empty.
        """
        Проверяет корректность данных перед сохранением.

        Проверяет наличие категории и жанра, если они предоставлены.
        """
        if 'category' in attrs and not attrs.get('category'):
            raise ValidationError('Необходимо указать категорию.')
        if 'genre' in attrs and not attrs.get('genre'):
            raise ValidationError('Необходимо указать хотя бы 1 жанр.')
        return attrs


class SignUpSerializer(serializers.Serializer):
    """
    Сериализатор для создания нового пользователя
    и отправки кода подтверждения.
    """
    username = serializers.CharField(
        max_length=MAX_LENGTH_USERNAME,
        validators=[UnicodeUsernameValidator(), validate_username])
    email = serializers.EmailField(max_length=MAX_LENGTH_EMAIL)

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

    def create(self, validated_data):
        return validated_data


class TokenObtainSerializer(serializers.Serializer):
    """
    Сериализатор для работы с токеном.
    """
    username = serializers.CharField(
        max_length=MAX_LENGTH_USERNAME,
        validators=[UnicodeUsernameValidator(), validate_username])
    confirmation_code = serializers.CharField(max_length=100)


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
        title = get_object_or_404(
            Title, id=self.context['view'].kwargs.get('title_id'))
        request = self.context['view'].request
        author = request.user
        if request.method == 'POST':
            if Review.objects.filter(author=author, title=title).exists(): 
                # Фильтруй сразу по ключу tite_id. Лишний запрос на 397 строке убираем.
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
