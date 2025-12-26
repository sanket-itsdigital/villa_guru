from django.contrib import admin
from .models import *

# Register your models here.

from .models import *

admin.site.register(amenity)
admin.site.register(customer_address)
admin.site.register(testimonials)


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
