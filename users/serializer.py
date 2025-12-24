
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import *
from masters.models import *
from masters.serializers import *


from customer.models import *


from rest_framework import serializers

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'firebase_uid',
            'mobile',
            'email',
            'profile_photo',

            'first_name',
            'last_name',
            'is_customer',
            'is_service_provider',
            # Add other fields only if they're on the User model
        ]
        read_only_fields = ['id', 'mobile', 'firebase_uid', 'is_customer', 'is_service_provider']
        extra_kwargs = {
            'firebase_uid': {'required': True},
            'email': {'required': False, 'allow_blank': True, 'allow_null': True},
        }
