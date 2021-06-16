from rest_framework.fields import EmailField
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
from rest_framework import status
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from . models import User


class EmailSerializer(serializers.Serializer):
    email = EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        user = User.objects.filter(email=email)
        if not user.exists():
            raise ParseError(detail=f'Пользователя {email} не существует')
        code = user[0]._gen_confirm_code()
        attrs.update({'confirmation_code': code})
        return attrs


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
