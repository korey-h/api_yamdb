from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .serializers import MyTokenObtainPairView
from .views import CommentViewSet, ReviewViewSet, TitleViewSet


# Создаётся роутер
router = DefaultRouter()
# Связываем URL с viewset, аналогично обычному path()
router.register('titles',
                TitleViewSet, basename="title")
router.register(r"titles/(?P<title_id>[^\/.]+)/reviews",
                ReviewViewSet, basename="review")
router.register(
    r"titles/(?P<title_id>[^/.]+)/reviews/(?P<review_id>[^/.]+)/comments",
    CommentViewSet, basename="comment")

urlpatterns = [
    path('v1/token/', MyTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('v1/auth/email/', views.SendConfirmEmailView.as_view()),
    path('v1/users/', views.UsersView.as_view(
        {'get': 'list', 'post': 'create'})
    ),
    path("v1/", include(router.urls)),
]
