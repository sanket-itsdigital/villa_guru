from django.urls import path

from .views import *

from django.conf import settings
from django.conf.urls.static import static




from rest_framework.routers import SimpleRouter

router = SimpleRouter()
# router.register(r'customer-address', customer_address_ViewSet, basename='test-booking')


urlpatterns = [

    path('vendor-dashboard/', vendor_dashboard, name='vendor_dashboard'),

    path('register-hotel/', register_hotel, name='register_hotel'),
    path('add-hotel/', add_hotel, name='add_hotel'),
    path('view-hotel/', view_hotel, name='view_hotel'),
    path('update-hotel/<hotel_id>', update_hotel, name='update_hotel'),
    path('delete-hotel/<hotel_id>', delete_hotel, name='delete_hotel'),
    path('list-hotel/', list_hotel, name='list_hotel'),

    path('delete-hotel-image/<int:image_id>/', delete_hotel_image, name='delete_hotel_image'),

    path('add-hotel-rooms/', add_hotel_rooms, name='add_hotel_rooms'),
    path('update-hotel-rooms/<hotel_rooms_id>', update_hotel_rooms, name='update_hotel_rooms'),
    path('delete-hotel-rooms/<hotel_rooms_id>', delete_hotel_rooms, name='delete_hotel_rooms'),
    path('view-hotel-rooms/<hotel_id>', view_hotel_rooms, name='view_hotel_rooms'),
    path('list-hotel-rooms/', list_hotel_rooms, name='list_hotel_rooms'),
    
    path('delete-hotel-room-image/<int:image_id>/', delete_hotel_room_image, name='delete_hotel_room_image'),
    
    path('list-hotel-bookings/', list_hotel_bookings, name='list_hotel_bookings'),
    path('list-hotel-future-bookings/', list_hotel_future_bookings, name='list_hotel_future_bookings'),
    path('update-hotel-bookings/<booking_id>', update_hotel_bookings, name='update_hotel_bookings'),
    path('view-hotel-bookings/<booking_id>', view_hotel_bookings, name='view_booking'),

    path('list-hotel-earning/', list_hotel_earning, name='list_hotel_earning'),
    path('hotel-invoice/<booking_id>', generate_invoice_pdf, name='render_pdf_view'),

    path('availability/update/', update_hotel_availability, name='update_hotel_availability'),
    path('availability/update-from-to/', update_from_to_hotel_availability, name='update_from_to_hotel_availability'),


]  + router.urls

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)