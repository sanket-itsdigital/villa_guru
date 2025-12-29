from django.contrib import admin
from .models import *

# Register your models here.

from .models import *

@admin.register(amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'image']
    search_fields = ['name']

@admin.register(property_type)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(city)
class CityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(villa_amenity)
class VillaAmenityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(room_type)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(villa_type)
class VillaTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

@admin.register(customer_address)
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'type', 'city', 'state', 'pin_code']
    list_filter = ['type', 'city', 'state']
    search_fields = ['user__mobile', 'user__email', 'name', 'address', 'city', 'state', 'pin_code']

@admin.register(testimonials)
class TestimonialsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

@admin.register(event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'amount', 'start_date', 'date_created']
    list_filter = ['start_date', 'date_created']
    search_fields = ['name', 'description']
    readonly_fields = ['date_created']
    date_hierarchy = 'start_date'

@admin.register(EventImage)
class EventImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'event', 'image']
    list_filter = ['event']
    search_fields = ['event__name']

@admin.register(home_banner)
class HomeBannerAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'is_for_web', 'is_active', 'created_at']
    list_filter = ['is_for_web', 'is_active', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(coupon)
class CouponAdmin(admin.ModelAdmin):
    """
    Admin interface for coupons/offers.
    Only superusers can add, change, or delete coupons.
    """
    list_display = ['code', 'title', 'type', 'discount_percentage', 'discount_amount', 'is_active', 'start_date', 'end_date']
    list_filter = ['type', 'is_active', 'start_date', 'end_date']
    search_fields = ['code', 'title', 'description']
    readonly_fields = []
    
    def has_add_permission(self, request):
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    """
    Admin interface for system settings.
    Only superusers can modify these settings.
    """

    def has_add_permission(self, request):
        # Only allow one settings instance
        if SystemSettings.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of settings
        return False

    list_display = ["price_markup_percentage", "updated_at", "created_at"]
    fields = ["price_markup_percentage"]
    readonly_fields = ["updated_at", "created_at"]
