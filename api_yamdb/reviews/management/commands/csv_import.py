import csv
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from reviews.models import Category, Comment, Genre, Title_genre, Review, Title

CSV_FILES_DIR = os.path.join(settings.BASE_DIR, 'static/data')

User = get_user_model()

CSV_FILES_MAPPING = {
    User: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    Title_genre: 'genre_title.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
}

FOREIGN_KEY_FIELDS = {
    'category': Category,
    'title': Title,
    'genre': Genre,
    'author': User,
    'review': Review,
}


class Command(BaseCommand):
    """
    Команда Django для импорта данных из CSV файлов в базу данных.

    Использование - `python manage.py csv_import`.

    Использует маппинг `CSV_FILES_MAPPING` для определения соответствия между
    моделями Django и именами CSV файлов. Ожидает, что CSV файлы находятся
    в директории, заданной переменной `CSV_FILES_DIR`.

    Для обработки внешних ключей используется словарь `FOREIGN_KEY_FIELDS`,
    где ключи - это имена полей внешних ключей (без '_id'), а значения -
    классы моделей, на которые ссылаются внешние ключи.

    Команда построчно читает CSV файлы, преобразует данные и создает
    соответствующие записи в базе данных для каждой модели, указанной
    в `CSV_FILES_MAPPING`.

    Выводит сообщения об успехе импорта для каждого файла и общее сообщение
    о завершении импорта в стандартный вывод. В случае, если CSV файл
    не найден в указанной директории, выбрасывает исключение `CommandError`.

    Attributes:
        help (str): Описание команды для отображения в `manage.py help`.
        requires_migrations_checks (bool): Указывает, что команда требует
            проверки наличия миграций перед выполнением.

    Methods:
        handle(*args, **options): Основной метод выполнения команды.
            Итерируется по `CSV_FILES_MAPPING`, обрабатывает каждый CSV файл
            и импортирует данные в соответствующую модель.
    """
    help = 'Импортирует данные из .csv файла'
    requires_migrations_checks = True

    def handle(self, *args, **options):
        for model, file_name in CSV_FILES_MAPPING.items():
            csv_file_path = os.path.join(CSV_FILES_DIR, file_name)
            if not os.path.exists(csv_file_path):
                raise CommandError(
                    f'Файл {file_name} не найден в директории {CSV_FILES_DIR}'
                )

            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data = {}
                    for field_name, value in row.items():
                        data_key = field_name.replace('_id', '')
                        if data_key in FOREIGN_KEY_FIELDS:
                            model_class = FOREIGN_KEY_FIELDS.get(data_key)
                            data[data_key] = model_class.objects.get(id=value)
                        else:
                            data[field_name] = value
                    model.objects.create(**data)
            self.stdout.write(self.style.SUCCESS(
                f'Данные из {file_name} успешно импортированы в '
                f'{model.__name__}'
            ))
        self.stdout.write(self.style.SUCCESS('Импорт завершен'))
