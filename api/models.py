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
    email = models.EmailField(
        unique=True,
        error_messages={'unique': ("A user with that email already exists.")}
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


class Title(models.Model):
    rating = models.FloatField(default=0)


class Review(models.Model):
    CHOICES = (
        (1, 'one'),
        (2, 'two'),
        (3, 'three'),
        (4, 'four'),
        (5, 'five'),
        (6, 'six'),
        (7, 'seven'),
        (8, 'eight'),
        (9, 'nine'),
        (10, 'ten')
    )
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name='reviews')
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews"
    )
    score = models.PositiveSmallIntegerField(choices=CHOICES)
    pub_date = models.DateTimeField(
        "Дата публикации", auto_now_add=True)

    def __str__(self):
        return self.text

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["title", "author"],
                                    name="unique_reviewing"), ]


class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    pub_date = models.DateTimeField("Дата добавления", auto_now_add=True)
