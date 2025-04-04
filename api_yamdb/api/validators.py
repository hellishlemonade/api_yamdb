from rest_framework import serializers


def validate_username_me(value):
    """
    Метод проверяющий поле на соответствие условию
    """
    if value.lower() == 'me':
        raise serializers.ValidationError(
            'Использование имени "me" под запретом.')
    return value
