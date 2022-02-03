from django.db import models
from django.contrib.auth import get_user_model
from .validators import validate_empty_field

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок'
    )

    slug = models.SlugField(
        unique=True,
        null=True
    )

    description = models.TextField(
        verbose_name='Описание',
    )

    def __str__(self):
        return self.title


class Post(models.Model):

    text = models.TextField(
        validators=[validate_empty_field],
        verbose_name='Текст поста'
    )

    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор поста'
    )

    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа'
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']
