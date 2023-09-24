from django.urls import path, include
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register(r'tier', TierViewSet, basename='tier')
router.register(r'explink', ExpLinkViewSet, basename='explink')
router.register(r'user', UserViewSet, basename='user')
router.register(r'image', ImageViewSet, basename='image')

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('', include(router.urls)),
]
