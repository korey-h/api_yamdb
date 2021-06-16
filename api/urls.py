from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .token_utils import MyTokenObtainPairView

urlpatterns = [
    path('v1/token/', MyTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('v1/auth/email/', views.SendConfirmEmailView.as_view()),
]
