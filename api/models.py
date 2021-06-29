from datetime import datetime, timedelta

import jwt.api_jwt
from api_yamdb import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_year

SCORE_MESSAGE = 'Оценка должна быть в диапазоне от 1 до 10'


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
    role = models.CharField(
        max_length=12,
        choices=Roles.choices,
        default=Roles.USER,
        verbose_name='Уровень прав пользователя'
    )

    def _gen_confirm_code(self):
        dt = datetime.now() + timedelta(days=1)
        return jwt.encode(payload={'id': self.pk, 'exp': dt.toordinal()},
                          key=settings.SECRET_KEY, algorithm='HS256')

    @property
    def is_admin(self):
        return self.role == Roles.ADMIN or self.is_staff or self.is_superuser


class Categories(models.Model):
    name = models.TextField(verbose_name='Название категории')
    slug = models.SlugField(unique=True)


class Genres(models.Model):
    name = models.TextField(verbose_name='Название жанра')
    slug = models.SlugField(unique=True)


class Titles(models.Model):
    name = models.TextField(verbose_name='Название произведения')
    year = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[validate_year],
        verbose_name='Год издания'
    )
    category = models.ForeignKey(
        Categories,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='titles',
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genres,
        blank=True,
        related_name='genres',
        verbose_name='Жанр'
    )
    description = models.TextField(
        null=True, blank=True,
        verbose_name='Описание'
    )


class Review(models.Model):
    title = models.ForeignKey(
        Titles,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Отзыв')
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=' Автор отзыва'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(1, message=SCORE_MESSAGE),
            MaxValueValidator(10, message=SCORE_MESSAGE)
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    def __str__(self):
        return self.text

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['title', 'author'],
                                    name='unique_reviewing'), ]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField(verbose_name='Комментарий')
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True
    )
