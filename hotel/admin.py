from django.contrib import admin

# Register your models here.


from .models import *

@admin.register(villa)
class VillaAdmin(admin.ModelAdmin):
    list_display = ['villa_id', 'name', 'user', 'city', 'category', 'price_per_night', 'markup_percentage', 'is_active', 'go_live', 'is_featured', 'created_at']
    list_filter = ['category', 'is_active', 'go_live', 'is_featured', 'is_recommended', 'city', 'property_type', 'villa_star_facility', 'created_at']
    search_fields = ['villa_id', 'name', 'user__mobile', 'user__email', 'address', 'city__name']
    readonly_fields = ['villa_id', 'created_at']
    filter_horizontal = ['amenities']
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Basic Information', {
            'fields': ('villa_id', 'user', 'name', 'category', 'property_type', 'description')
        }),
        ('Location', {
            'fields': ('city', 'address', 'landmark', 'pincode')
        }),
        ('Pricing', {
            'fields': ('price_per_night', 'markup_percentage', 'profit_margin')
        }),
        ('Features', {
            'fields': ('amenities', 'no_of_rooms', 'star_rating', 'overall_rating', 'villa_star_facility', 'main_image')
        }),
        ('Status & Visibility', {
            'fields': ('is_active', 'go_live', 'is_featured', 'is_recommended')
        }),
        ('Legal & Tax Info', {
            'fields': ('gst_number', 'gst_certificate', 'pan_number')
        }),
        ('Bank Details', {
            'fields': ('account_holder_name', 'account_number', 'ifsc_code', 'bank_name', 'bank_document')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

@admin.register(VillaImage)
class VillaImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'villa', 'image']
    list_filter = ['villa']
    search_fields = ['villa__name', 'villa__villa_id']

@admin.register(villa_rooms)
class VillaRoomsAdmin(admin.ModelAdmin):
    list_display = ['id', 'villa', 'room_type', 'title', 'price_per_night', 'max_guest_count', 'refundable', 'meals_included']
    list_filter = ['villa', 'room_type', 'title', 'refundable', 'meals_included']
    search_fields = ['villa__name', 'villa__villa_id', 'room_type__name', 'description']
    filter_horizontal = ['villa_amenities']

@admin.register(villa_roomsImage)
class VillaRoomsImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'villa_rooms', 'image']
    list_filter = ['villa_rooms__villa']
    search_fields = ['villa_rooms__villa__name']

@admin.register(VillaAvailability)
class VillaAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['id', 'villa', 'date', 'is_open']
    list_filter = ['is_open', 'date', 'villa']
    search_fields = ['villa__name', 'villa__villa_id']
    date_hierarchy = 'date'

@admin.register(RoomAvailability)
class RoomAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['id', 'room', 'date', 'available_count']
    list_filter = ['date', 'room__villa']
    search_fields = ['room__villa__name', 'room__room_type__name']
    date_hierarchy = 'date'

@admin.register(VillaPricing)
class VillaPricingAdmin(admin.ModelAdmin):
    list_display = ['id', 'villa', 'date', 'price_per_night', 'created_at', 'updated_at']
    list_filter = ['villa', 'date', 'created_at']
    search_fields = ['villa__name', 'villa__villa_id']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']