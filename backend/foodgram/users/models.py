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


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_follow')
        ]

    def __str__(self):
        return f'{self.user} follows {self.following}'
