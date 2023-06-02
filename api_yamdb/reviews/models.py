from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.validators import (
    MaxValueValidator,
    MinLengthValidator,
    )
from django.db import models
from django.db.models import TextField

from api.validation import validate_year

class Role:
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


ROLE_CHOICE = (
    (Role.USER, "Пользователь"),
    (Role.MODERATOR, "Модератор"),
    (Role.ADMIN, "Администратор"),
)


class User(AbstractUser):
    username = models.CharField(
        max_length=150, unique=True, validators=(ASCIIUsernameValidator,)
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
    )
    email = models.EmailField(
        unique=True,
        max_length=254,
        blank=True,
    )
    bio = models.TextField(blank=True)
    role = models.CharField(
        max_length=10, null=False, choices=ROLE_CHOICE, default=Role.USER
    )
    is_active = models.BooleanField(default=True)

    @property
    def is_admin(self):
        return self.role == Role.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == Role.MODERATOR

    REQUIRED_FIELDS = ["email"]


class Category(models.Model):
    name = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ('id', )

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ('id', )

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.PositiveSmallIntegerField(validators=[validate_year])
    description = models.TextField(blank=True, null=True)
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        through='TitleGenre',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True
    )

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'
        ordering = ('id', )

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=''
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Author'
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            MinLengthValidator(1, 'min rate 1'),
            MaxValueValidator(10, 'max rate 10')
        ],
        verbose_name='Rate'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique review'
            )
        ]
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ('-pub_date', )

    def __str__(self) -> TextField:
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Review'
    )
    text = models.TextField(verbose_name='Text')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Author'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Pub_date'
    )

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.text


class TitleGenre(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    class Meta:
        ordering = ('id', )

    def __str__(self):
        return f'{self.genre} {self.title}'
