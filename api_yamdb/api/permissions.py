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
        return (
            request.user.is_superuser 
            #Атрибут is_superuser нужно учесть в методе is_admin. Тут и далее.
            or (request.user.is_authenticated and request.user.is_admin())
        )


class ContentManagePermission(permissions.BasePermission):
    """
    Права доступа к контенту: ресурсы reviews и comments.

    Изменение постов и комментариев доступно следующим категориям ползователей:
    Автор поста/комментария, Модератор, Администратор, Суперпользователь.
    """
    message = 'Недостаточно прав.'

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return any([ 
            # Лишняя функция.
            request.method in permissions.SAFE_METHODS,
            (request.user.is_authenticated and obj.author == request.user), 
            # Не повторяйся. Проверяем аутентификацию один раз в выражении.
            # Можно лучше:
            # Проверку требующую запрос в БД лучше размещать в самом конце,
            # для того, чтобы если остальные проверки не дали False лишний запрос в БД бы не совершался.
            (request.user.is_authenticated and request.user.is_moderator()),
            (request.user.is_authenticated and request.user.is_admin())
        ])


class IsAdminPermission(permissions.BasePermission):
    """
    Пермишен, дающий право доступа к эндпоинту только пользователю
    со статусом admin.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.is_superuser or request.user.is_admin()))


class IsUserPermissions(permissions.BasePermission):
    """
    Право доступа к своему аккаунту и внесение изменений
    в свой аккаунт.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj
