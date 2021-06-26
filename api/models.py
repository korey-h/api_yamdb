import jwt.api_jwt

from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from api_yamdb import settings


class Roles(models.TextChoices):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'


class CustomUser(AbstractUser):

    email = models.EmailField(
        unique=True,
        error_messages={'unique': ('A user with that email already exists.')}
    )
    bio = models.TextField(max_length=250, null=True, blank=True,
                           verbose_name='Информация о себе')
    role = models.CharField(max_length=12,
                            choices=Roles.choices,
                            default='user',
                            verbose_name='Уровень прав пользователя')

    def _gen_confirm_code(self):
        dt = datetime.now() + timedelta(days=1)
        return jwt.encode(payload={'id': self.pk, 'exp': dt.toordinal()},
                          key=settings.SECRET_KEY, algorithm='HS256')


User = get_user_model()


class Categories(models.Model):
    name = models.TextField(verbose_name='Название категории')
    slug = models.SlugField(unique=True)


class Genres(models.Model):
    name = models.TextField(verbose_name='Название жанра')
    slug = models.SlugField(unique=True)


class Titles(models.Model):
    name = models.TextField(verbose_name='Название произведения')
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    category = models.ForeignKey(
        Categories,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='titles'
    )
    genre = models.ManyToManyField(
        Genres,
        blank=True,
        related_name='genres'
    )
    description = models.TextField(
        null=True, blank=True,
        verbose_name='Описание'
    )
    # rating = models.FloatField(default=None, null=True, blank=True, )


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
    title = models.ForeignKey(Titles, on_delete=models.CASCADE,
                              related_name='reviews')
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews'
    )
    score = models.PositiveSmallIntegerField(choices=CHOICES)
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True)

    def __str__(self):
        return self.text

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['title', 'author'],
                                    name='unique_reviewing'), ]


class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField(verbose_name='Комментарий')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments'
    )
    pub_date = models.DateTimeField('Дата добавления', auto_now_add=True)
