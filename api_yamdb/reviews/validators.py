from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value):
    """Проверяет, что год не больше текущего года."""
    current_year = timezone.now().year
    if value > current_year:
        raise ValidationError(
            f'Год {value} больше текущего года {current_year}.',
            params={'year': value},
        )
