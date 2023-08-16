from typing import Any, Final
# from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from django.core.mail import send_mail
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone


from core.models import FoodgramModelMixin


class FoodgramUserManager(BaseUserManager):

    def _create_user(self, username, email, password, first_name, last_name,
                     **other):
        if not username:
            raise ValueError('The given username must be set')
        if not email:
            raise ValueError('The given email must be set')
        if not first_name:
            raise ValueError('The given first_name must be set')
        if not last_name:
            raise ValueError('The given last_name must be set')
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            **other
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password,
                    first_name, last_name, **other):
        other.setdefault('is_staff', False)
        other.setdefault('is_superuser', False)
        return self._create_user(
            username, email, password, first_name, last_name, **other)

    def create_superuser(self, username, email, password,
                         first_name, last_name, **other):
        other.setdefault('is_staff', True)
        other.setdefault('is_superuser', True)
        if other.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if other.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(
            username, email, password, first_name, last_name, **other)


class FoodgramUser(AbstractBaseUser,
                   PermissionsMixin,
                   FoodgramModelMixin):

    USERNAME_MAX_LENGTH: Final[int] = 150
    FIRST_NAME_MAX_LENGTH: Final[int] = 150
    LAST_NAME_MAX_LENGTH: Final[int] = 150

    username = models.CharField(
        verbose_name='Username',
        max_length=USERNAME_MAX_LENGTH,
        unique=True
    )

    email = models.EmailField(
        verbose_name='Email address',
        unique=True
    )

    first_name = models.CharField(
        verbose_name='First name',
        max_length=FIRST_NAME_MAX_LENGTH
    )

    last_name = models.CharField(
        verbose_name='Last name',
        max_length=LAST_NAME_MAX_LENGTH
    )

    is_staff = models.BooleanField(
        verbose_name='Staff status',
        default=False
    )

    is_active = models.BooleanField(
        verbose_name='Active status',
        default=True
    )

    date_joined = models.DateTimeField(
        verbose_name='Date joined',
        default=timezone.now
    )

    subscriptions = models.ManyToManyField(
        to='self',
        through='Subscription',
        symmetrical=False
    )

    objects = FoodgramUserManager()

    USERNAME_FIELD = 'username'

    EMAIL_FIELD = 'email'

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def get_full_name(self) -> str:
        return f'{self.first_name} {self.last_login}' or self.username

    def get_short_name(self) -> str:
        return self.first_name or self.username

    def is_admin(self) -> bool:
        return self.is_active and (self.is_superuser or self.is_staff)

    @classmethod
    def clear_data(cls) -> None:
        cls.objects.filter(is_superuser=False).delete()

    @classmethod
    def import_data(cls, data: dict[str, Any]) -> 'FoodgramUser':
        return cls.objects.create_user(**data)

    @classmethod
    def export_queryset(cls) -> QuerySet:
        return cls.objects.filter(is_superuser=False)

    @classmethod
    def export_fieldnames(cls) -> tuple[str]:
        return ('id', 'username', 'email', 'first_name', 'last_name')

    @classmethod
    def export_data(cls, instance: 'FoodgramUser') -> dict[str, Any]:
        return {
            'id': instance.id,
            'username': instance.username,
            'email': instance.email,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
        }


class Subscription(models.Model, FoodgramModelMixin):

    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=FoodgramUser,
        on_delete=models.CASCADE,
        related_name='subscription_source'
    )

    author = models.ForeignKey(
        verbose_name='Автор',
        to=FoodgramUser,
        on_delete=models.CASCADE,
        related_name='subscription_target'
    )

    class Meta:
        verbose_name = 'Подписка пользователя'
        verbose_name_plural = 'Подписки пользователей'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription',
            ),
        ]
        ordering = ('id',)

    def __str__(self) -> str:
        return f'{self.user} <-> {self.author}'

    @classmethod
    def import_data(cls, data: dict[str, Any]) -> 'Subscription':
        return cls.objects.create(**data)

    @classmethod
    def export_fieldnames(cls) -> tuple[str]:
        return ('id', 'user_id', 'author_id')

    @classmethod
    def export_data(cls, instance: 'Subscription') -> dict[str, Any]:
        return {
            'id': instance.id,
            'user_id': instance.user_id,
            'author_id': instance.author_id,
        }
