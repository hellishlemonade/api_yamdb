from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    SignUpViewSet,
    TitleViewSet,
    TokenViewSet,
    UserAdminViewSet,
)

VERSION = 'v1'
AUTH = 'auth'


router = SimpleRouter()
# Имя роутера должно содержать номер версии нашей API.
# Так избавимся от путаницы при появлении новых версий.
# Добавь префикс с номером версии к имени переменной.
router.register('titles', TitleViewSet, basename='titles')
router.register('genres', GenreViewSet, basename='genres')
router.register('categories', CategoryViewSet, basename='categories')
router.register(f'{AUTH}/signup', SignUpViewSet)
router.register(f'{AUTH}/token', TokenViewSet)
router.register('users', UserAdminViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments')

urlpatterns = [
    path(f'{VERSION}/', include(router.urls)),
]
