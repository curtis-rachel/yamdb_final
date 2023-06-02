from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.validators import ASCIIUsernameValidator

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.validation import validate_year
from reviews.models import Comment, Category, Genre, Review, Title


User = get_user_model()
REGEX = r"^[\w.@+-]+\Z"


class ReviewSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField()
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
        model = Review

    def validate_score(self, value):
        if value < 0 or value > 10:
            raise serializers.ValidationError('Введите значение от 1 до 10')
        return value

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        if (
                request.method == 'POST'
                and Review.objects.filter(title_id=title_id,
                                          author=author).exists()
        ):
            raise ValidationError('Отзыв уже оставлен')
        return data


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, max_length=254)
    username = serializers.RegexField(
        REGEX,
        required=True,
        max_length=150,
    )

    def validate(self, attrs):
        if attrs["username"] == "me":
            raise ValidationError("Нельзя me для username")
        return attrs


class TokenSeriliazer(serializers.Serializer):
    username = serializers.CharField(
        required=True, validators=(ASCIIUsernameValidator,)
    )
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        max_length=254,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
        ],
    )
    username = serializers.RegexField(
        REGEX,
        required=True,
        validators=(
            UniqueValidator(queryset=User.objects.all()),
        ),
        max_length=150,
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "bio",
            "role",
        )


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(
        slug_field='text',
        queryset=Review.objects.all()
    ),
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitleSafeSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False)
    genre = GenreSerializer(many=True)
    rating = serializers.IntegerField(read_only=True, initial=0)
    year = serializers.IntegerField(validators=(validate_year,))

    class Meta:
        fields = '__all__'
        model = Title


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='slug',
                                            queryset=Category.objects.all())
    genre = serializers.SlugRelatedField(slug_field='slug',
                                         many=True,
                                         queryset=Genre.objects.all())
    year = serializers.IntegerField(validators=(validate_year,))

    class Meta:
        fields = '__all__'
        model = Title
