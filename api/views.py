from django.core.mail import send_mail
from rest_framework import filters, status, pagination, permissions
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .models import User
from .serializers import EmailSerializer, PatchUserSerializer, UserSerializer


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
        return request.user.role == 'admin' or request.user.is_staff

    def has_permission(self, request, view):
        return request.user.role == 'admin' or request.user.is_staff


class UsersView(GetPostViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin, ]
    queryset = User.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', ]
    pagination_class = pagination.PageNumberPagination


class EditUserView(ModelViewSet):
    serializer_class = PatchUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = User.objects.all()
    lookup_field = 'username'
    lookup_url_kwarg = 'username'


class EditSelfView(ModelViewSet):
    serializer_class = PatchUserSerializer

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        serializer.save(role=self.request.user.role, )
