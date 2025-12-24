from django.contrib import admin
from .models import *

# Register your models here.

from .models import *

admin.site.register(amenity)
admin.site.register(coupon)
admin.site.register(customer_address)
admin.site.register(testimonials)


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
