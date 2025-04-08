from django.urls import include, path


VERSION = 'v1'

urlpatterns = [
    path(f'{VERSION}/', include('api.v1.urls')),
]
