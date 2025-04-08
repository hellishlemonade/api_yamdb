from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    AuthViewSet,
    TitleViewSet,
    UserAdminViewSet,
)

VERSION = 'v1'
AUTH = 'auth'


v1_router = SimpleRouter()
v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register(f'{AUTH}', AuthViewSet, basename=f'{AUTH}')
v1_router.register('users', UserAdminViewSet)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments')

urlpatterns = [
    path(f'{VERSION}/', include(v1_router.urls)),
    # Общий префикс v1 описываем api.urls.
]
