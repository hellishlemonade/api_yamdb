from django.urls import include, path
from rest_framework.routers import SimpleRouter


from .views import CategoryViewSet, GenreViewSet, TitleViewSet, SignUpViewSet, TokenViewSet

VERSION = 'v1'

router = SimpleRouter()
router.register('titles', TitleViewSet, basename='titles')
router.register('genres', GenreViewSet, basename='genres')

router.register('categories', CategoryViewSet, basename='categories')
router.register('auth', SignUpViewSet)
router.register('token', TokenViewSet)

urlpatterns = [
    path(f'{VERSION}/', include(router.urls)),
]
