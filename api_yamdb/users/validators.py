from django.core.exceptions import ValidationError


FORBIDDEN_ME = 'me'
FORBIDDEN_NICKNAMES = [FORBIDDEN_ME]


def validate_username(value):
    """
    Метод проверяющий поле на соответствие условию.
    """
    if value.lower() in FORBIDDEN_NICKNAMES:
        raise ValidationError(
            f'Использование имени "{value}" под запретом.')
    return True
