import secrets

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class CustomUser(AbstractUser):
    """
    Кастомная модель юзера. Содержит дополнительные поля, расширяющие
    дефолтную модель, такие как: "confirmation_code", ""bio", "role".
    """
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    USERS = [
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    ]

    password = models.CharField(
        'Пароль',
        max_length=150,
        blank=True,
        null=True)

    username = models.CharField(
        'Никнейм',
        max_length=150,
        unique=True,
        blank=False,
        null=False)

    email = models.EmailField(
        'Email',
        max_length=254,
        unique=True,
        blank=False,
        null=False,
        validators=[validate_email])

    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=100,
        blank=False,
        null=False)

    bio = models.CharField(
        'Описание',
        max_length=254,
        blank=True,
        null=True)

    role = models.CharField(
        'Роль',
        max_length=10,
        choices=USERS,
        default=USER,
        blank=False,
        null=False)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def clean(self):
        super().clean()
        if self.username.lower() == 'me':
            raise ValidationError('Использование имени "me" под запретом.')
        if not self.email:
            raise ValidationError('Email обязателен для заполнения.')

    def save(self, *args, **kwargs):
        if not self.confirmation_code:
            self.confirmation_code = secrets.token_urlsafe(16)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
