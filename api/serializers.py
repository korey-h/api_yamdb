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
        self.user = get_object_or_404(User,
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


class TitlesDetailSerializer(serializers.ModelSerializer):
    category = CategoriesSerializer()
    genre = GenresSerializer(many=True, )

    class Meta:
        fields = '__all__'
        model = Titles


class TitlesCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(queryset=Categories.objects.all(),
                                            slug_field='slug')
    genre = serializers.SlugRelatedField(many=True,
                                         queryset=Genres.objects.all(),
                                         slug_field='slug')

    class Meta:
        fields = '__all__'
        model = Titles
        extra_kwargs = {'name': {'required': True}, }

    def to_representation(self, obj):
        self.fields['category'] = CategoriesSerializer()
        self.fields['genre'] = GenresSerializer(many=True)
        return super(TitlesCreateSerializer, self).to_representation(obj)


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
        fields = '__all__'
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        exclude = ['review', ]
        model = Comment
