import secrets

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class CustomUser(AbstractUser):
    # Не используем в названиях слова Custom или My.
    # Они подходят только для учебных примеров, но не для реального кода.
    """
    Кастомная модель юзера. Содержит дополнительные поля, расширяющие
    дефолтную модель, такие как: "confirmation_code", ""bio", "role".
    """
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    USERS = [
        # Используем TextChoice.
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    ]

    password = models.CharField(
        # Уже наследовали.
        'Пароль',
        max_length=150,
        blank=True,
        null=True)

    username = models.CharField(
        # Нужно добавить валидаторы:
        # Для валидации символов есть готовый валидатор UnicodeUsernameValidator() из django.contrib.auth.validators.
        # Задачка со звездочкой: Можно переписать готовый валидатор символов на кастомный,
        # чтобы отдавать пользователю сообщение о том, какие конкретно символы нас не устроили.
        # Нужно добавить валидацию для ника me.
        'Никнейм',
        max_length=150,
        unique=True,
        blank=False,
        # blank=False и null=False - это дефолтный параметр. Описывать явно не нужно. 
        # Тут и далее.
        null=False)

    email = models.EmailField(
        'Email',
        max_length=254,
        # Это значение(254) по-умолчанию установлено в models.EmailField.
        unique=True,
        blank=False,
        null=False,
        validators=[validate_email])
        # Валидатор уже описан в поле EmailField 

    confirmation_code = models.CharField(
        # Код в БД не храним.
        'Код подтверждения',
        max_length=100,
        blank=False,
        null=False)

    bio = models.CharField(
        'Описание',
        max_length=254,
        # Нет ограничений по ТЗ.
        blank=True,
        null=True)
        # Для текстовых полей не стоит использовать null=True.
        # Объяснения посмотрите в документации - там хорошо раскрыта причина.

    role = models.CharField(
        'Роль',
        max_length=10,
        # Завтра добавим новую роль super-puper-moderator и длины строк уже не хватить. Резервируем побольше ресурсов.
        # Все значения ограничений берем из констант.
        choices=USERS,
        default=USER,
        blank=False,
        null=False)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def clean(self):
        # Лишний метод.
        super().clean()
        if self.username.lower() == 'me':
            raise ValidationError('Использование имени "me" под запретом.')
        if not self.email:
            raise ValidationError('Email обязателен для заполнения.')

    def save(self, *args, **kwargs):
        if not self.confirmation_code:
            self.confirmation_code = secrets.token_urlsafe(16)
        super().save(*args, **kwargs)

    def is_user(self):
        # Где используется?
        """Проверяет, является ли пользователь аутентифицированным."""
        return self.role == self.USER

    def is_moderator(self):
        """Проверяет, является ли пользователь модератором."""
        return self.role == self.MODERATOR

    def is_admin(self):
        """Проверяет, является ли пользователь администратором."""
        return (self.role == self.ADMIN
                or self.is_superuser)  # пока сделал так, меняйте, если что

    def __str__(self):
        # По такому строковому представлению не понятно к какому объекту оно принадлежит.
        # Строковое представление делаем более содержательным.
        return self.username
