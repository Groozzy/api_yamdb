from django.utils.translation import gettext_lazy
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        USER = 'user', gettext_lazy('user')
        MODERATOR = 'moderator', gettext_lazy('moderator')
        ADMIN = 'admin', gettext_lazy('admin')

    role = models.CharField(max_length=40,
                            choices=Roles.choices,
                            default=Roles.USER)
    email = models.EmailField(max_length=60, blank=False, unique=True)
    bio = models.TextField(max_length=250, blank=True)

    def save(self, *args, **kwargs):
        if self.role == 'moderator':
            self.is_staff = True
        if self.role == 'admin':
            self.is_superuser = True
        super(User, self).save(*args, **kwargs)

    @property
    def is_admin(self):
        return self.role == self.Roles.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.Roles.MODERATOR

    @property
    def is_user(self):
        return self.role == self.Roles.USER
