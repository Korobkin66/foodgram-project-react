from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = models.CharField(verbose_name='Логин',
                                max_length=200,
                                unique=True)
    email = models.EmailField(verbose_name='Электронная Почта',
                              max_length=200,
                              unique=True)
    password = models.CharField(verbose_name='Пароль',
                                max_length=200)

    def __str__(self):
        return self.username
