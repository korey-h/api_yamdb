from django.urls import path
# from rest_framework.routers import DefaultRouter

from . import views
from .serializers import MyTokenObtainPairView

urlpatterns = [
    path('v1/token/', MyTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('v1/auth/email/', views.SendConfirmEmailView.as_view()),
    path('v1/users/', views.UsersView.as_view(
        {'get': 'list', 'post': 'create'})
    )
]
