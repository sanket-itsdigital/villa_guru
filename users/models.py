from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, mobile, password=None, **extra_fields):
        """Create and return a regular user with a mobile number and password."""
        if not mobile:
            raise ValueError("The Mobile field must be set")
        user = self.model(mobile=mobile, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(mobile, password, **extra_fields)

class User(AbstractUser):

    firebase_uid = models.CharField(max_length=128, unique=True, null=True, blank=True)
    
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)

    is_customer = models.BooleanField(default=False)
    is_service_provider = models.BooleanField(default=False)

    mobile = models.CharField(max_length=15, unique=True)
    email = models.EmailField(
        unique=True,
        null=True,       # allow NULL in database
        blank=True       # allow empty form field
    )
    # Email is optional

    email_verified = models.BooleanField(default=False)
    
    # Property type for vendors (one vendor can have only one property type)
    property_type = models.ForeignKey(
        "masters.property_type",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vendors",
        help_text="Property type for vendor (Villa, Resort, or Couple Stay). One vendor can have only one property type."
    )

    username = None  # Remove username field

    USERNAME_FIELD = 'mobile'  # Set mobile as the login field
    REQUIRED_FIELDS = [] 

    objects = CustomUserManager()



