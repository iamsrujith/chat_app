from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from multiselectfield import MultiSelectField

INTEREST_CHOICES = (('food', 'food'),
                    ('travel', 'travel'),
                    ('movies', 'movies'),
                    ('hiking', 'hiking'),
                    ('cars', 'cars'))

GENDER = (('male', 'male'),
          ('female', 'female'),
          ('others', 'others'))


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("You have not provided a valid e-mail address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=255, blank=True, default='')
    email = models.EmailField(blank=True, default='', unique=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    gender = models.CharField(choices=GENDER, max_length=20)
    interests = MultiSelectField(choices=INTEREST_CHOICES,
                                 max_choices=3,
                                 max_length=100)

    is_online = models.BooleanField(default=False)
    in_chat = models.BooleanField(default=False)
    is_ready = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email