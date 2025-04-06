from django.contrib.auth import get_user_model
from django.db import models

from .validators import validate_year

User = get_user_model()

RATING_VALUES = [(i, str(i)) for i in range(1, 11)]

# Общий комментарий
# Проверить и добавить для всех моделей:
# verbose-поля также нужно настроить у всех моделей (verbose_name и verbose_name_plural)
# ordering также должно быть в каждой модели
# строковое представление __str__


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
        max_length=256,
        # Для всех дублирующихся размеров текстовых полей в моделях и сериализаторах нужно завести константы в settings.py.
        # Тут и далее все значения ограничений берем из констант.
        help_text='Название произведения',
        db_index=True,  # поиск по имени произведения - частая операция
    )
    year = models.IntegerField(
        # SmallIntegerField
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
        through='Title_genre',
        # Точно такую же модель для m2m поля Джанго создаст самостоятельно. 
        # Лишнее.
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

    def __str__(self):
        # По такому строковому представлению не понятно к какому объекту оно принадлежит.
        # Строковое представление делаем более содержательным.
        # Тут и далее по всем моделям.
        return self.name


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
        max_length=256,
        help_text='Название жанра'
    )
    slug = models.SlugField(
        verbose_name='Слаг жанра',
        max_length=50,
        help_text='Уникальный слаг жанра',
        unique=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title_genre(models.Model):
    # На будущее:
    # Классы мы пишем в стиле CamelCase.
    # Можешь посмотреть в гайдлайне нотацию для остальных типов.
    """
    Модель для представления связи между жанрами и произведениями.

    Поля:
        title (ForeignKey): Связь с моделью Title.
        genre (ForeignKey): Связь с моделью Genre.

    Методы:
        __str__: Возвращает строковое представление: название - жанр.
    """
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='title_genre'
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        related_name='title_genre'
    )

    def __str__(self):
        return f'{self.title} - {self.genre}'


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
        max_length=256,
        help_text='Название категории'
    )
    slug = models.SlugField(
        verbose_name='Слаг категории',
        max_length=50,
        help_text='Уникальный слаг категории',
        unique=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Review(models.Model):
    """
    Модель для представления отзывов на произведения.
    """
    text = models.TextField()
    score = models.IntegerField(choices=RATING_VALUES)
    # SmallIntegerField
    # choices лишний.
    # Нужно учесть что значение у нас не меньше 1 и не более 10.
    # Настраиваем валидацию через атрибут validators и используем готовые валидаторы MinValueValidator и MaxValueValidator.
    # Параметром message, в каждом классе валидации, можно указать сообщение с причиной данной ошибки.
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True, db_index=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews'
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews'
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        # Модель нужно привести в порядок, согласно код-стайлу джанго.
        # -   All database fields
        # -   Custom manager attributes
        # -   class Meta
        # -   def __str__()
        # -   def save()
        # -   def get_absolute_url()
        # -   Any custom methods
        # Внимание на очередность.
        ordering = ('pub_date', 'title')
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'], name='unique_review'),
        ]


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

    def __str__(self):
        return self.text[:15]

    class Meta:
        # См.  222.
        ordering = ('pub_date', 'review')
