from django.contrib.auth.models import AbstractUser
from django.db import models

CHOICES = (('user', 'user'),
           ('moderator', 'moderator'),
           ('admin', 'admin'))


class User(AbstractUser):
    role = models.CharField(max_length=40, choices=CHOICES, default='user')
    email = models.EmailField(max_length=60, blank=False, unique=True)
    bio = models.TextField(max_length=250, blank=True)

    def save(self, *args, **kwargs):
        if self.role == 'moderator':
            self.is_staff = True
        if self.role == 'admin':
            self.is_superuser = True
        super(User, self).save(*args, **kwargs)
