from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg, fields, ExpressionWrapper
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken

from api.filters import MyTitleFilter
from api.mixins import ListCreateDeleteViewSet
from api.pagination import MyPaginator
from api.permissions import (IsAdmin,
                             IsAdminModeratorAuthorOrReadOnly,
                             IsAdminOrReadOnly)
from api.serializers import (SignUpSerializer, TokenSeriliazer, UserSerializer,
                             CommentSerializer, ReviewSerializer,
                             CategorySerializer, GenreSerializer,
                             TitleSerializer, TitleSafeSerializer)
from reviews.models import Title, Review, Comment, Category, Genre


User = get_user_model()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [
        IsAdmin,
    ]
    lookup_field = "username"
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    http_method_names = ["get", "post", "delete", "patch"]

    @action(
        detail=False,
        methods=["GET", "PATCH"],
        url_path="me",
        permission_classes=[
            permissions.IsAuthenticated,
        ],
    )
    def get_current_user(self, request):
        if request.method == "GET":
            serializer = UserSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role, partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username_exists = User.objects.filter(
        username=serializer.validated_data["username"]
    ).exists()
    email_exists = User.objects.filter(
        email=serializer.validated_data["email"]
    ).exists()
    if email_exists and not username_exists:
        return Response(
            {"detail": "email exist"}, status=status.HTTP_400_BAD_REQUEST
        )
    if not email_exists and username_exists:
        return Response(
            {"detail": "username exist"}, status=status.HTTP_400_BAD_REQUEST
        )

    user, _ = User.objects.get_or_create(
        username=serializer.validated_data["username"],
        email=serializer.validated_data["email"],
    )
    confirmation_code = default_token_generator.make_token(user)
    user.email_user(
        subject="Код подтверждения",
        message=f"Ваш код - {confirmation_code}",
        from_email="admin@admin.ru",
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def token(request):
    serializer = TokenSeriliazer(data=request.data)
    if serializer.is_valid():
        user = get_object_or_404(
            User, username=serializer.validated_data["username"]
        )
        confirmation_code = serializer.validated_data["confirmation_code"]
        if default_token_generator.check_token(user, confirmation_code):
            access_token = AccessToken.for_user(user)
            data = {
                "username": request.data["username"],
                "token": str(access_token),
            }
            return Response(data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_value(self, field, title=None):
    value_id = self.kwargs.get(f'{field}')
    if title:
        value = get_object_or_404(Review, id=value_id, title=title)
        return value
    value = get_object_or_404(Title, id=value_id)
    return value


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,
                        title=get_value(self, 'title_id'))

    def get_queryset(self):
        return get_value(self, 'title_id').reviews.all()


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)

    def review(self):
        title = get_value(self, 'title_id')
        return get_value(self, 'review_id', title=title)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.review())

    def get_queryset(self):
        return Comment.objects.filter(review=self.review())


class CategoryViewSet(ListCreateDeleteViewSet):
    queryset = Category.objects.get_queryset().order_by('id')
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = MyPaginator
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)

    def destroy(self, request, *args, **kwargs):
        category = get_object_or_404(Category, slug=kwargs['pk'])
        self.perform_destroy(category)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenreViewSet(ListCreateDeleteViewSet):
    queryset = Genre.objects.get_queryset().order_by('id')
    serializer_class = GenreSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)

    def destroy(self, request, *args, **kwargs):
        genre = get_object_or_404(Genre, slug=kwargs['pk'])
        self.perform_destroy(genre)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.prefetch_related("reviews").annotate(
        rating=ExpressionWrapper(
            Avg("reviews__score"),
            output_field=fields.IntegerField()
        )
    )
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = MyTitleFilter

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update', 'destroy'):
            return TitleSerializer
        return TitleSafeSerializer
