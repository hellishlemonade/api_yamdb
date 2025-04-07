from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator

from .validators import validate_username


MAX_LENGTH_USERNAME = 150
MAX_LENGTH_ROLE = 100


class UserProfile(AbstractUser):
    """
    Кастомная модель юзера. Содержит дополнительные поля, расширяющие
    дефолтную модель, такие как: "bio", "role".
    """
    class UsersRole(models.TextChoices):
        USER = 'user'
        MODERATOR = 'moderator'
        ADMIN = 'admin'

    username = models.CharField(
        'Никнейм',
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
        validators=[UnicodeUsernameValidator(), validate_username]
    )

    email = models.EmailField(
        'Email',
        unique=True
    )

    bio = models.TextField(
        'Описание',
        blank=True,
    )

    role = models.CharField(
        'Роль',
        max_length=MAX_LENGTH_ROLE,
        choices=UsersRole.choices,
        default=UsersRole.USER,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def is_moderator(self):
        """Проверяет, является ли пользователь модератором."""
        return self.role == self.UsersRole.MODERATOR

    def is_admin(self):
        """Проверяет, является ли пользователь администратором."""
        return self.role == self.UsersRole.ADMIN or self.is_superuser

    def __str__(self):
        return (
            f'username: {self.username},'
            f'email: {self.email}.'
        )
