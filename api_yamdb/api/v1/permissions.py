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
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated and request.user.is_admin())


class ContentManagePermission(permissions.IsAuthenticatedOrReadOnly):
    """
    Права доступа к контенту: ресурсы reviews и comments.

    Изменение постов и комментариев доступно следующим категориям ползователей:
    Автор поста/комментария, Модератор, Администратор, Суперпользователь.
    """
    message = 'Недостаточно прав.'

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and (obj.author == request.user
                     or request.user.is_moderator()
                     or request.user.is_admin()))


class IsAdminPermission(permissions.BasePermission):
    """
    Пермишен, дающий право доступа к эндпоинту только пользователю
    со статусом admin.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin()


class IsUserPermissions(permissions.BasePermission):
    """
    Право доступа к своему аккаунту и внесение изменений
    в свой аккаунт.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj
