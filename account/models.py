from typing import Any
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, phone_number,username, password=None, **extra_fields):
        if not email:
            raise ValueError("user must have an email address")
        if not phone_number:
            raise ValueError("user must have a phone number")
        if User.objects.filter(phone_number=phone_number).exists():
            raise ValueError("User with this phone number already exists")
            
        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number,username=username, **extra_fields)
        user.set_password(password)
        user.is_active=True
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, phone_number, username=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_admin", True)
        return self.create_user(email, phone_number, username, password, **extra_fields)
    

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length= 100)
    email = models.EmailField(max_length= 100,unique=True)
    phone_number = models.CharField(max_length= 15,unique=True)
    tfa_secret = models.CharField(max_length= 50, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username','phone_number']
    
    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    def get_name(self):
        return f"Name: {self.username}"

    def __str__(self):
        return self.phone_number