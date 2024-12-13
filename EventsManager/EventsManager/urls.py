from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, UserRegistrationAPIView, CustomAuthToken

router = DefaultRouter()
router.register(r'events', EventViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationAPIView.as_view(), name='user-register'),
    path('token/', CustomAuthToken.as_view(), name='api-token-auth'),
]
