from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .serializers import MyTokenObtainPairView

router_v1 = DefaultRouter()
router_v1.register('categories', views.CategoriesView, basename='categories')
router_v1.register('genres', views.GenreViews, basename='genres')
router_v1.register('titles', views.TitleViews, basename='titles')
router_v1.register(r'titles/(?P<title_id>[^\/.]+)/reviews',
                   views.ReviewViewSet, basename='review')
router_v1.register(
    r'titles/(?P<title_id>[^/.]+)/reviews/(?P<review_id>[^/.]+)/comments',
    views.CommentViewSet, basename='comment')
router_v1.register('users', views.UserView, basename='users')
url_auth = [
    path('token/', MyTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('email/', views.SendConfirmEmailView.as_view())
]

urlpatterns = [
    path('v1/auth/', include(url_auth)),
    path('v1/', include(router_v1.urls)),
]
