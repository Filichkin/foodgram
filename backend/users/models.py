from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from foodgram.constants import (
    EMAIL_MAX_LENGTH,
    FIRST_NAME_MAX_LENGTH,
    LAST_NAME_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    USERNAME_MAX_LENGTH
)


class User(AbstractUser):
    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        blank=False,
        null=False,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Username contains restricted symbols. Please use only '
                    'letters, numbers and .@+- symbols',
        ), ],
        verbose_name='Unique username',
    )
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Email address',
    )
    first_name = models.CharField(
        max_length=FIRST_NAME_MAX_LENGTH,
    )
    last_name = models.CharField(
        max_length=LAST_NAME_MAX_LENGTH,
    )
    password = models.CharField(
        min_length=PASSWORD_MIN_LENGTH,
    )
    avatar = models.ImageField(
        blank=True,
        null=True,
        upload_to='media/avatars/',
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password',
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username']

    def __str__(self):
        return self.username
    

class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Author'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow'
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='check_not_self_follow',
            ),
        )

    def __str__(self):
        return f'Subscribe: {self.user.username} for {self.author.username}'
