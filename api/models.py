from datetime import datetime, timedelta
import jwt
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from api_yamdb import settings


class CustomUser(AbstractUser):

    AUTH_USER_ROLES = (
        ('user', 'user'),
        ('admin', 'admin'),
        ('moderator', 'moderator')
    )
    bio = models.TextField(max_length=250, null=True, blank=True)
    role = models.CharField(max_length=12,
                            choices=AUTH_USER_ROLES,
                            default='user')

    def _gen_confirm_code(self):
        dt = datetime.now() + timedelta(days=1)
        return jwt.encode({'id': self.pk, 'exp': dt.toordinal()},
                          settings.SECRET_KEY, algorithm='HS256')


User = get_user_model()
