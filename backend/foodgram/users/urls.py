from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet

app_name = 'users'

router = DefaultRouter()

router.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('auth/', include("djoser.urls.authtoken")),
    path('api/', include(router.urls)),
    path('', include('djoser.urls')),
    path('', include(router.urls)),
]

# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import UserViewSet

# router = DefaultRouter()
# router.register(r'users', UserViewSet, basename='user')

# urlpatterns = [
#     path('api/', include(router.urls)),
# ]
