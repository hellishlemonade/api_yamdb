from django.core.exceptions import ValidationError

from api_yamdb.settings import FORBIDDEN_NICKNAMES


def validate_username(value):
    """
    Метод проверяющий поле на соответствие условию.
    """
    if value.lower() in FORBIDDEN_NICKNAMES:
        raise ValidationError(
            f'Использование имени "{value}" под запретом.')
