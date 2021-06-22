import django_filters
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, pagination, permissions
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.exceptions import PermissionDenied

from .filters import TitleFilter
from .models import Categories, Genres, Review, Titles, User
from .permissions import (IsAdmin, IsOwnerOrAdminOrModeratorOrReadOnly,
                          IsAdminOrReadOnly)
from .serializers import (
    CommentSerializer, CategoriesSerializer, EmailSerializer,
    GenresSerializer, PatchUserSerializer,
    ReviewSerializer, TitlesDetailSerializer, TitlesCreateSerializer,
    UserSerializer)


class DestroyViews(DestroyModelMixin,
                   GenericViewSet):
    pass


class GetPostViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
    pass


class SendConfirmEmailView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        data = EmailSerializer(data=request.data)
        if data.is_valid():
            message = ('confirmation_code:'
                       f' {data.validated_data["confirmation_code"]}')
            destination = data.validated_data['email']
            send_mail(
                'e-mail confirmation',
                message,
                'auth@yambdb.com',
                [destination, ],
                fail_silently=False,
            )
            return Response({'detail': 'email was sent'},
                            status=status.HTTP_200_OK)
        return Response(data=data.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersView(GetPostViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin, ]
    queryset = User.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', ]
    pagination_class = pagination.PageNumberPagination


class EditUserView(ModelViewSet):
    serializer_class = PatchUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin, ]
    queryset = User.objects.all()
    lookup_field = 'username'
    lookup_url_kwarg = 'username'


class EditSelfView(ModelViewSet):
    serializer_class = PatchUserSerializer

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        serializer.save(role=self.request.user.role, )


class CategoriesView(ModelViewSet):
    queryset = Categories.objects.all()
    http_method_names = ['get', 'post', ]
    serializer_class = CategoriesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    pagination_class = pagination.PageNumberPagination


class DeleteCategoryViews(DestroyViews):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin, ]
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'


class GenreViews(ModelViewSet):
    queryset = Genres.objects.all()
    http_method_names = ['get', 'post', ]
    serializer_class = GenresSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    pagination_class = pagination.PageNumberPagination


class DeleteGenreViews(ModelViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin, ]
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'


class TitleViews(ModelViewSet):
    queryset = Titles.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = TitlesDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsAdminOrReadOnly]
    pagination_class = pagination.PageNumberPagination
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return TitlesCreateSerializer
        return self.serializer_class

class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsOwnerOrAdminOrModeratorOrReadOnly,
                          permissions.IsAuthenticatedOrReadOnly, )
    pagination_class = pagination.PageNumberPagination

    def perform_create(self, serializer):
        title = get_object_or_404(Titles, id=self.kwargs['title_id'])
        serializer.save(title=title, author=self.request.user)
        # пересчитываем и сохраняем рейтинг после сохранения отзыва
        title.rating = title.reviews.aggregate(Avg('score'))['score__avg']
        title.save(update_fields=['rating', ])

    def perform_update(self, serializer):
        title = get_object_or_404(Titles, id=self.kwargs['title_id'])
        serializer.save(title=title, author=self.request.user)
        # пересчитываем и сохраняем рейтинг после сохранения отзыва
        title.rating = title.reviews.aggregate(Avg('score'))['score__avg']
        title.save(update_fields=['rating', ])

    def get_queryset(self):
        title = get_object_or_404(Titles, id=self.kwargs['title_id'])
        return title.reviews.all()


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsOwnerOrAdminOrModeratorOrReadOnly,
                          permissions.IsAuthenticatedOrReadOnly, )
    pagination_class = pagination.PageNumberPagination

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs["review_id"])
        serializer.save(review=review, author=self.request.user)

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs["review_id"])
        return review.comments.all()
