from django.contrib import admin

# Register your models here.


from .models import *

@admin.register(VillaBooking)
class VillaBookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'user', 'villa', 'booking_type', 'check_in', 'check_out', 'status', 'payment_status', 'total_amount', 'created_at']
    list_filter = ['booking_type', 'status', 'payment_status', 'payment_type', 'created_at']
    search_fields = ['booking_id', 'user__mobile', 'user__email', 'villa__name', 'first_name', 'last_name', 'phone_number', 'email']
    readonly_fields = ['booking_id', 'created_at']
    date_hierarchy = 'created_at'
    inlines = []

@admin.register(BookingRoom)
class BookingRoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'room', 'quantity', 'price_per_night']
    list_filter = ['booking__booking_type', 'booking__status']
    search_fields = ['booking__booking_id', 'room__room_type__name', 'room__villa__name']
    readonly_fields = ['price_per_night']

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'booking', 'subject', 'is_resolved', 'created_at']
    list_filter = ['is_resolved', 'created_at']
    search_fields = ['user__mobile', 'user__email', 'subject', 'booking__booking_id']
    readonly_fields = ['created_at']

@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'ticket', 'sender', 'created_at']
    list_filter = ['created_at']
    search_fields = ['ticket__subject', 'sender__mobile', 'sender__email', 'message']
    readonly_fields = ['created_at']

@admin.register(favouritevilla)
class FavouriteVillaAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'villa']
    list_filter = ['villa']
    search_fields = ['user__mobile', 'user__email', 'villa__name']

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'amount', 'status', 'method', 'razorpay_payment_id', 'created_at']
    list_filter = ['status', 'method', 'created_at']
    search_fields = ['booking__booking_id', 'razorpay_order_id', 'razorpay_payment_id']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

@admin.register(VillaReview)
class VillaReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'villa', 'rating', 'created_at', 'updated_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__mobile', 'user__email', 'villa__name', 'comment']
    readonly_fields = ['created_at', 'updated_at']