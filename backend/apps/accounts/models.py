import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManger(BaseUserManager):
    use_in_migrations = True 

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("User must have an email address.")
        
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user 
    
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra_fields)
    


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(unique=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD= "email"
    REQUIRED_FIELDS = []

    objects = UserManger()

    class Meta:
        db_table = "user"

    def __str__(self):
        return self.email
