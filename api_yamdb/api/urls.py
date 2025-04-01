from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import TitleViewSet

VERSION = 'v1'

router = SimpleRouter()
router.register('titles', TitleViewSet, basename='titles')

urlpatterns = [
    path(f'{VERSION}/', include(router.urls)),
]
