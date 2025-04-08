from django.core.exceptions import ValidationError


FORBIDDEN_ME = 'me'
# Лишняя константа.
FORBIDDEN_NICKNAMES = [FORBIDDEN_ME]
# В settings.


def validate_username(value):
    """
    Метод проверяющий поле на соответствие условию.
    """
    if value.lower() in FORBIDDEN_NICKNAMES:
        raise ValidationError(
            f'Использование имени "{value}" под запретом.')
    return True
    # Возвращаемое значение не используется.
