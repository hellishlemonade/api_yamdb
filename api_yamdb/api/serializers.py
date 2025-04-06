import secrets

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.core.validators import RegexValidator
from rest_framework.exceptions import status
from rest_framework import serializers
from rest_framework.exceptions import NotFound, status
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.settings import DEFAULT_FROM_EMAIL
from reviews.models import (
    Category, Comment, Genre, RATING_VALUES, Review, Title)
from .validators import validate_username_me


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
        exclude = ('id',)
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
        exclude = ('id', )


class TitleReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения данных произведения (Title).

    Используется для получения информации о произведении.
    """
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True, default=None)
    # Тут хватит IntegerField,
    # в котором надо будет указать
    # параметр default (дефолтом будет None).

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category', 'rating')
        # Модель может измениться, а с такой настройкой наш АПИ
        # уже не будет соответствовать спецификации.
        # Описываем явно поля.
        # Тут и далее.

    '''def get_rating(self, obj):
        # Такой подход породит множество запросов в БД (отдельный запрос для каждого элемента QuerySet).
        # Нужно изменить подход: добавьте атрибут rating для всех элементов QuerySet путем его аннотирования во вью.
        """
        Возвращает средний рейтинг произведения.

        Если произведение не имеет отзывов, возвращает 0.
        """
        annotated_title = Title.objects.annotate(
            rating=Avg('reviews__score')
        ).get(pk=obj.pk)
        return annotated_title.rating or None'''


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

    '''def validate(self, attrs):
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
        return attrs'''


class SignUpSerializer(serializers.ModelSerializer): 
    # Этот сериализатор нам нужен будет только для валидации, создавать юзера через него не нужно. Письма отправляются во вью. Наследуемся от обычного serializers.Serializer.
    # Нужно описать каждое поле явно указав все требуемые ограничения - длину строк и валидаторы (атрибут validators).
    # -- Для валидации символов есть готовый валидатор UnicodeUsernameValidator() из django.contrib.auth.validators.
    # -- Не забыть про валидатор для ника me
    # Валидацию для комбинации ника и почты описываем в методе validate.
    """
    Сериализатор для создания нового пользователя
    и отправки кода подтверждения.
    """
    class Meta:
        model = User
        fields = ['email', 'username']
        extra_kwargs = {
            'email': {
                'required': True,
                'validators': []
            },
            'username': {
                'required': True,
                'validators': [RegexValidator(r'^[\w.@+-]+\Z')]
            }
        }

    def validate_username(self, value):
        """
        Метод проверяющий поле "username" на соответствие условию
        создания юзернеймов.
        """
        return validate_username_me(value)

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
                    {'email':
                     ERROR_EMAIL})
            else:
                return data
        if username_exists:
            raise ValidationError(
                {'username': ERROR_USERNAME})
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
                # Общий комментарий по проверочному коду:
                # Способ создания и проверки кода неплохой, но есть еще более подходящий стандартный default_token_generator, в котором даже хранить confirmatiom_code не нужно.
                # Для создания кода используй default_token_generator.make_token из from django.contrib.auth.tokens import default_token_generator прокидывая в него объект юзера.
                # Для проверки токена используй функцию default_token_generator.check_token прокидывая в неё юзера и проверочный код.
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
    # Постоянные величины ограничений берем из констант.
    # Добавить валидаторы. См. 130 п.2.
    confirmation_code = serializers.CharField(max_length=100, required=True)

    def validate(self, attrs):
        username = attrs.get('username')
        confirmation_code = attrs.get('confirmation_code')
        try: 
            # get_object_or_404
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound(
                detail=ERROR_USERNAME,
                code=status.HTTP_404_NOT_FOUND)
        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код подверждения.'})
        attrs['token'] = str(AccessToken.for_user(user)) 
        # Сериализатор только проверяет поля. Всю логику представления описываем во вью.
        # У сериализатора только 2 поля и подмешивать другие в методы которые за это не отвечают не лучшая идея.
        # Варианта 2 на выбор:
        # Либо проверку кода вынести во вью
        # Либо во вью нужно будет второй раз сходить за юзером чтобы отдать токен
        return attrs

    def to_representation(self, instance): # Лишний метод.
        return {'token': instance['token']}

    def create(self, validated_data): 
        # Это не модельный сериализатор. Созданием не занимаемся.
        return validated_data


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для выполнения CRUD операций с моделью CustomUser
    """
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'bio', 'role']
        extra_kwargs = { 
            # Лишняя настройка. 
            # Так как это модельный сериализатор, то все настройки полей (включая валидацию) он подтянет из модели автоматически.
            # Описывать поля/настройки/валидаторы нет необходимости если мы ничего не меняем.
            'email': {
                'required': False
            },
            'username': {
                'required': False,
                'validators': [RegexValidator(r'^[\w.@+-]+\Z')]
            }
        }

    def validate_username(self, value): 
        # Все методы сериализатора лишние по той же причине
        """
        Метод проверяющий поле "username" на соответствие условию
        создания юзернеймов.
        """
        return validate_username_me(value)

    def validate(self, data):
        if 'username' not in data:
            raise ValidationError(
                {'username': ERROR_REQUIRED_VALUE}
            )
        if 'email' not in data:
            raise ValidationError(
                {'email': ERROR_REQUIRED_VALUE}
            )
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError(
                {'username': ERROR_USERNAME}
            )
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                {'email': ERROR_EMAIL}
            )
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=None,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', 'user'),
            bio=validated_data.get('bio', '')
        )
        return user


class UserUpdateSerializer(serializers.ModelSerializer): 
    # Лишний сериализатор. В нем та же самая логика что и в сериализаторе выше.
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'bio', 'role']

    def validate_username(self, value):
        """
        Метод проверяющий поле "username" на соответствие условию
        создания юзернеймов.
        """
        return validate_username_me(value)

    def validate(self, attrs):
        if 'username' in attrs:
            if User.objects.filter(username=attrs['username']).exists():
                raise serializers.ValidationError(
                    {'username': ERROR_USERNAME}
                )
        if 'email' in attrs:
            if User.objects.filter(email=attrs['email']).exists():
                raise serializers.ValidationError(
                    {'email': ERROR_EMAIL}
                )
        return attrs


class MeSerializer(serializers.ModelSerializer): 
    # Лишнее.
    """
    Сериализатор для выполнения операций получения экземпляра
    и внесения изменений в собственный профиль.
    """
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'bio', 'role']
        read_only_fields = ['role']
        extra_kwargs = {
            'username': {
                'required': True,
                'validators': [RegexValidator(r'^[\w.@+-]+\Z')]
            }
        }

    def validate_username(self, value): 
        # Этот и следующий метод лишние.
        """
        Метод проверяющий поле "username" на соответствие условию
        создания юзернеймов.
        """
        return validate_username_me(value)

    def validate(self, data):
        if 'username' not in data:
            return data
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError(
                {'username': ERROR_USERNAME}
            )
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                {'email': ERROR_EMAIL}
            )
        return data


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
