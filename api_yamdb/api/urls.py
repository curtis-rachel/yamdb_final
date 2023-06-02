from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet, UserViewSet, signup, token)

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
router.register(r'titles/(?P<title_id>\d+)/reviews',
                ReviewViewSet, basename='reviews')
router.register(
    'categories', CategoryViewSet, basename='categories')
router.register(
    'genres', GenreViewSet, basename='genres'
)
router.register(
    'titles', TitleViewSet, basename='titles'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments'
)

authurls = [
    path("signup/", signup, name="signup"),
    path("token/", token, name="token"),
]

urlpatterns = [
    path("v1/", include(router.urls)),
    path("v1/auth/", include(authurls)),
]
