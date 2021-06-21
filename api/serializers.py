from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.fields import EmailField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Categories, Comment, Genres, Review, Titles, User


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = get_user_model().EMAIL_FIELD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['confirmation_code'] = serializers.CharField(required=True)
        self.fields.pop('password')

    def validate(self, attrs):
        self.user = get_object_or_404(get_user_model(),
                                      email=attrs[self.username_field])
        data = {}

        if not self.user._gen_confirm_code() == attrs['confirmation_code']:
            raise ParseError(detail='Confirmation code is wrong or expired.')

        refresh = super().get_token(self.user)
        data['token'] = str(refresh.access_token)

        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


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


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('first_name', 'last_name', 'username', 'bio',
                  'email', 'role')
        model = User


class PatchUserSerializer(serializers.ModelSerializer):

    class Meta:
        extra_kwargs = {'username': {'required': False},
                        'email': {'required': False}, }
        fields = ('first_name', 'last_name', 'username', 'bio',
                  'email', 'role')
        model = User


class CategoriesSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Categories


class GenresSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genres


class TitlesSerializer(serializers.ModelSerializer):
    category = CategoriesSerializer(read_only=False, required=False)
    genre = GenresSerializer(many=True, read_only=False, required=False)

    class Meta:
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre', 'category')
        model = Titles
        extra_kwargs = {'name': {'required': True}, }

    def create(self, validated_data):
        genres_data = validated_data.pop('genre', None)
        genres_data = self.initial_data.getlist('genre')
        category_slug = self.initial_data.get('category')
        category = Categories.objects.get_or_create(slug=category_slug)
        title = Titles.objects.create(**validated_data)
        title.category = category[0]

        for slug in genres_data:
            genre = Genres.objects.get_or_create(slug=slug)
            title.genre.add(genre[0])
            title.save()

        return title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True

    )
    title = serializers.SlugRelatedField(
        slug_field='id',
        read_only=True
    )

    def validate(self, data):
        if self.context['request'].method == 'POST':
            author = self.context['request'].user
            title = self.context['view'].kwargs['title_id']
            review = Review.objects.filter(author=author, title=title)
            if review:
                raise ValidationError('Вы уже оставили свой отзыв')
        return data

    class Meta:
        fields = ("id", "text", "author", "score", "pub_date", "title")
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = ("id", "text", "author", "pub_date")
        model = Comment
