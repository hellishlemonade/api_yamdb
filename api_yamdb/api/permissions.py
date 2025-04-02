from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает доступ на чтение всем пользователям,
    но только администраторам на запись, обновление и удаление.

    Права доступа определяются следующим образом:
    - GET, HEAD, OPTIONS запросы разрешены всем пользователям.
    - POST, PUT, PATCH, DELETE запросы разрешены только аутентифицированным
      пользователям с ролью 'администратор' (is_admin = True).

    Используется для ViewSet'ов, которые должны быть доступны для чтения всем,
    но изменяться только администраторами.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin()
