from django.db import models

from .validators import validate_year


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
        help_text='Название произведения',
        db_index=True,  # поиск по имени произведения - частая операция
    )
    year = models.IntegerField(
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

    def __str__(self):
        return self.name
