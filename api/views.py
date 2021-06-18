from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .models import Review, Title, User
from .permissions import IsOwnerOrAdminOrModeratorOrReadOnly
from .serializers import (
    CommentSerializer,
    EmailSerializer,
    ReviewSerializer,
    TitleSerializer,
    UserSerializer)


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


class GetPostViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
    pass


class IsAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.role == 'admin'


class UsersView(GetPostViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAdmin, permissions.IsAuthenticated]
    queryset = User.objects.all()


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsOwnerOrAdminOrModeratorOrReadOnly,
                          permissions.IsAuthenticatedOrReadOnly, )

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        serializer.save(title=title, author=self.request.user)
        # пересчитываем и сохраняем рейтинг после сохранения отзыва
        title.rating = title.reviews.aggregate(Avg('score'))['score__avg']
        title.save(update_fields=['rating', ])

    def perform_update(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        serializer.save(title=title, author=self.request.user)
        # пересчитываем и сохраняем рейтинг после сохранения отзыва
        title.rating = title.reviews.aggregate(Avg('score'))['score__avg']
        title.save(update_fields=['rating', ])

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        return title.reviews.all()


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsOwnerOrAdminOrModeratorOrReadOnly,
                          permissions.IsAuthenticatedOrReadOnly, )

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs["review_id"])
        serializer.save(review=review, author=self.request.user)

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs["review_id"])
        return review.comments.all()


class TitleViewSet(ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
