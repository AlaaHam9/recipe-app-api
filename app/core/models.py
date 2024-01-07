from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    PermissionsMixin,
    AbstractBaseUser
)

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_feilds):
        if not email:
            raise ValueError('User mist have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_feilds)
        user.set_password(password)
        user.save(using=self.db) # to support multi db
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff= True
        user.is_superuser = True
        user.save(using=self.db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    email       = models.EmailField(max_length=255, unique=True)
    name        = models.CharField(max_length=255)
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)

    objects     = UserManager() # sign the user manager

    USERNAME_FIELD = 'email'
