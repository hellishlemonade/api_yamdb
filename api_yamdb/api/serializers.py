from rest_framework import serializers
from django.core.exceptions import ValidationError

from reviews.models import Genre, Title


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
    genre = GenreSerializer(read_only=True)
    category = CategorySerializer(read_only=True)  # заглушка
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

        Проверяет наличие категории и жанра.
        """
        if not attrs.get('category'):
            raise ValidationError('Необходимо указать категорию.')
        if not attrs.get('genre'):
            raise ValidationError('Необходимо указать хотя бы 1 жанр.')
        return attrs
