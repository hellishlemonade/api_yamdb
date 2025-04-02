from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import GenreViewSet, TitleViewSet

VERSION = 'v1'

router = SimpleRouter()
router.register('titles', TitleViewSet, basename='titles')
router.register('genres', GenreViewSet, basename='genres')

urlpatterns = [
    path(f'{VERSION}/', include(router.urls)),
]
