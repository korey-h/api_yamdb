import re

from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, pagination, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .filters import TitleFilter
from .models import Categories, Genres, Review, Titles, User
from .permissions import (IsAdmin, IsOwnerOrAdminOrModeratorOrReadOnly,
                          IsAdminOrReadOnly)
from .serializers import (
    CommentSerializer, CategoriesSerializer, EmailSerializer,
    GenresSerializer, PatchUserSerializer,
    ReviewSerializer, TitlesDetailSerializer, TitlesCreateSerializer,
    UserSerializer)


class SendConfirmEmailView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        data = EmailSerializer(data=request.data)
        if data.is_valid():
            email = data.validated_data['email']
            user = User.objects.get_or_create(email=email)
            if user[0].username == '':
                name = re.search(r'.*(?=@)', email)
                setattr(user[0], 'username', name[0])
                user[0].save()
            confirmation_code = user[0]._gen_confirm_code()
            message = (f'confirmation_code: {confirmation_code}')
            destination = email
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


class UserView(ModelViewSet):
    serializer_class = PatchUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin, ]
    queryset = User.objects.all()
    lookup_field = 'username'
    lookup_url_kwarg = 'username'
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', ]
    pagination_class = pagination.PageNumberPagination

    def personal_info(self):
        username = self.kwargs.get('username', None)
        return username and (username == 'me')

    def _allowed_methods(self):
        if self.personal_info():
            self.http_method_names = ['get', 'patch']
        return super()._allowed_methods()

    def get_permissions(self):
        if self.personal_info():
            return [permissions.IsAuthenticated(), ]
        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        if self.kwargs == {}:
            return UserSerializer
        return self.serializer_class

    def get_object(self):
        if self.personal_info():
            return self.request.user
        return super().get_object()

    def perform_update(self, serializer):
        if self.personal_info():
            serializer.validated_data['role'] = self.request.user.role
        serializer.save()


class CategoriesView(ModelViewSet):
    queryset = Categories.objects.all()
    http_method_names = ['delete', 'get', 'post', ]
    serializer_class = CategoriesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    pagination_class = pagination.PageNumberPagination
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'

    def _allowed_methods(self):
        if self.kwargs != {}:
            self.http_method_names = ['delete', ]
        return super()._allowed_methods()


class GenreViews(ModelViewSet):
    queryset = Genres.objects.all()
    http_method_names = ['get', 'post', ]
    serializer_class = GenresSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    pagination_class = pagination.PageNumberPagination
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'

    def _allowed_methods(self):
        if self.kwargs != {}:
            self.http_method_names = ['delete', ]
        return super()._allowed_methods()


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
        review = get_object_or_404(Review, id=self.kwargs['review_id'])
        serializer.save(review=review, author=self.request.user)

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs['review_id'])
        return review.comments.all()
