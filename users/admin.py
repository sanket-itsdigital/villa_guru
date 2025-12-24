from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import *  # Import your custom form


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = (
        'mobile', 'first_name', 'last_name', 'email',
        'is_staff', 'is_active',
        'is_customer', 'is_service_provider'
    )
    list_filter = (
        'is_staff', 'is_active',
        'is_customer', 
    )

    fieldsets = (
        (None, {
            'fields': (
                'mobile', 'email', 'first_name', 'last_name',
                'password', 'firebase_uid'
            )
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_active', 'is_superuser')
        }),
        ('Roles', {
            'fields': ('is_customer', 'is_service_provider', )
        }),
        ('Groups & Permissions', {
            'fields': ('groups', 'user_permissions')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'mobile', 'email', 'first_name', 'last_name',
                'password1', 'password2',
                'is_staff', 'is_active'
            )
        }),
    )

    search_fields = ('mobile', 'first_name', 'last_name', 'email')
    ordering = ('mobile',)

admin.site.register(User, CustomUserAdmin)