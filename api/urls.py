from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .serializers import MyTokenObtainPairView

router = DefaultRouter()
router.register('categories', views.CategoriesView, basename='categories')
router.register('titles', views.TitlesView, basename='titles')
router.register(r"titles/(?P<title_id>[^\/.]+)/reviews",
                views.ReviewViewSet, basename="review")
router.register(
    r"titles/(?P<title_id>[^/.]+)/reviews/(?P<review_id>[^/.]+)/comments",
    views.CommentViewSet, basename="comment")

urlpatterns = [
    path('v1/token/', MyTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('v1/auth/email/', views.SendConfirmEmailView.as_view()),
    path('v1/users/me/', views.EditSelfView.as_view(
        {'get': 'retrieve', 'patch': 'update'})
    ),
    path('v1/users/<str:username>/', views.EditUserView.as_view(
        {'get': 'retrieve', 'patch': 'update', 'delete': 'destroy'})
    ),
    path('v1/users/', views.UsersView.as_view(
        {'get': 'list', 'post': 'create'})
    ),
    path('v1/genres/<str:slug>/', views.DeleteGenreViews.as_view(
        {'delete': 'destroy', })
    ),
    path('v1/genres/', views.GenreViews.as_view(
        {'get': 'list', 'post': 'create'})
    ),
    path('v1/categories/<str:slug>/', views.DeleteCategoryViews.as_view(
        {'delete': 'destroy'})
    ),
    path('v1/categories/', views.CategoriesView.as_view(
        {'get': 'list', 'post': 'create'})
    ),
    path('v1/', include(router.urls)),
]
