from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from api_yamdb.settings import (
    DEFAULT_NAME_LENGTH,
    DEFAULT_SLUG_LENGTH,
    REVIEW_MIN_SCORE,
    REVIEW_MAX_SCORE
)
from .validators import validate_year

User = get_user_model()


class Title(models.Model):
    """
    Модель произведения.

    Представляет собой произведение, такое как фильм, книга или песня.
    Содержит информацию о названии, годе создания, описании,
    жанре и категории произведения.

    Атрибуты:
        name (CharField): Название произведения. Обязательное поле,
                          максимальная длина 256 символов.
                          Индексируется для быстрого поиска.
        year (IntegerField): Год создания произведения. Обязательное поле.
                             Проходит валидацию,
                             чтобы год не был больше текущего.
        description (TextField): Описание произведения. Необязательное поле,
                                 может быть пустым.
        genre (ManyToManyField): Жанры произведения. Связь "многие-ко-многим" с
                                 моделью Genre. Может быть несколько жанров.
        category (ForeignKey): Категория произведения. Связь "один-ко-многим" с
                               моделью Category. Указывает на категорию,
                               к которой относится произведение.
                               При удалении связанной категории,
                               устанавливается значение NULL.

    Meta:
        verbose_name (str): Человекочитаемое имя в единственном числе.
        verbose_name_plural (str): Человекочитаемое имя во множественном числе.

    Методы:
        __str__(): Возвращает строковое представление произведения - название.
    """
    name = models.CharField(
        verbose_name='Название',
        max_length=DEFAULT_NAME_LENGTH,
        help_text='Название произведения',
        db_index=True,
    )
    year = models.SmallIntegerField(
        verbose_name='Год создания',
        help_text='Год создания произведения',
        validators=[validate_year]
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Описание произведения',
        blank=True,
    )
    genre = models.ManyToManyField(
        'Genre',
        verbose_name='Жанр',
        help_text='Жанр произведения',
        related_name='titles',
    )
    category = models.ForeignKey(
        'Category',
        verbose_name='Категория',
        help_text='Категория произведения',
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self):
        return f'{self.category} {self.name}'


class Genre(models.Model):
    """
    Модель для представления жанров произведений.

    Поля:
        name (CharField): Название жанра.
        slug (SlugField): Уникальный слаг жанра, используется в URL.

    Метаданные:
        verbose_name (str): Человекочитаемое имя в единственном числе.
        verbose_name_plural (str): Человекочитаемое имя во множественном числе.

    Методы:
        __str__: Возвращает строковое представление жанра - название.
    """
    name = models.CharField(
        verbose_name='Название жанра',
        max_length=DEFAULT_NAME_LENGTH,
        help_text='Название жанра'
    )
    slug = models.SlugField(
        verbose_name='Слаг жанра',
        max_length=DEFAULT_SLUG_LENGTH,
        help_text='Уникальный слаг жанра',
        unique=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return f'Жанр {self.name}'


class Category(models.Model):
    """
    Модель для представления категорий произведений.

    Поля:
        name (CharField): Название категории.
        slug (SlugField): Уникальный слаг категории, используется в URL.

    Метаданные:
        verbose_name (str): Человекочитаемое имя в единственном числе.
        verbose_name_plural (str): Человекочитаемое имя во множественном числе.

    Методы:
        __str__: Возвращает строковое представление категории - название.
    """
    name = models.CharField(
        verbose_name='Название категории',
        max_length=DEFAULT_NAME_LENGTH,
        help_text='Название категории'
    )
    slug = models.SlugField(
        verbose_name='Слаг категории',
        max_length=DEFAULT_SLUG_LENGTH,
        help_text='Уникальный слаг категории',
        unique=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return f'Категория {self.name}'


class Review(models.Model):
    """
    Модель для представления отзывов на произведения.
    """
    text = models.TextField()
    score = models.SmallIntegerField(
        validators=[
            MinValueValidator(
                REVIEW_MIN_SCORE,
                f"Оценка на может быть меньше {REVIEW_MIN_SCORE}"
            ),
            MaxValueValidator(
                REVIEW_MAX_SCORE,
                f"Оценка на может быть больше {REVIEW_MAX_SCORE}"
            )
        ]
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True, db_index=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews'
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews'
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('pub_date', 'title')
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'], name='unique_review'),
        ]

    def __str__(self):
        return f"{self.id} отзыв на произведение {self.title.name}."


class Comment(models.Model):
    """
    Модель для представления комментариев на отзывы пользователей.
    """
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments'
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments'
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True, db_index=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('pub_date', 'review')

    def __str__(self):
        return f"Комментарий №{self.id} к отзыву на {self.title.name}."
