from django.urls import path

from .views import *

from django.conf import settings
from django.conf.urls.static import static


from rest_framework.routers import SimpleRouter

router = SimpleRouter()
# router.register(r'customer-address', customer_address_ViewSet, basename='test-booking')


urlpatterns = [
    path("vendor-dashboard/", vendor_dashboard, name="vendor_dashboard"),
    path("register-villa/", register_hotel, name="register_villa"),
    path("add-villa/", add_hotel, name="add_villa"),
    path("view-villa/", view_hotel, name="view_villa"),
    path("update-villa/<villa_id>", update_hotel, name="update_villa"),
    path("delete-villa/<villa_id>", delete_hotel, name="delete_villa"),
    path("list-villa/", list_hotel, name="list_villa"),
    path(
        "delete-villa-image/<int:image_id>/",
        delete_hotel_image,
        name="delete_villa_image",
    ),
    path("add-villa-rooms/", add_hotel_rooms, name="add_villa_rooms"),
    path(
        "update-villa-rooms/<villa_rooms_id>",
        update_hotel_rooms,
        name="update_villa_rooms",
    ),
    path(
        "delete-villa-rooms/<villa_rooms_id>",
        delete_hotel_rooms,
        name="delete_villa_rooms",
    ),
    path("view-villa-rooms/<villa_id>", view_hotel_rooms, name="view_villa_rooms"),
    path("list-villa-rooms/", list_hotel_rooms, name="list_villa_rooms"),
    path(
        "delete-villa-room-image/<int:image_id>/",
        delete_hotel_room_image,
        name="delete_villa_room_image",
    ),
    path("list-villa-bookings/", list_hotel_bookings, name="list_villa_bookings"),
    path(
        "list-villa-future-bookings/",
        list_hotel_future_bookings,
        name="list_villa_future_bookings",
    ),
    path(
        "update-villa-bookings/<booking_id>",
        update_hotel_bookings,
        name="update_villa_bookings",
    ),
    path(
        "view-villa-bookings/<booking_id>",
        view_hotel_bookings,
        name="view_villa_booking",
    ),
    path("list-villa-earning/", list_hotel_earning, name="list_villa_earning"),
    path("villa-invoice/<booking_id>", generate_invoice_pdf, name="render_pdf_view"),
    path(
        "availability/update/",
        update_hotel_availability,
        name="update_villa_availability",
    ),
    path(
        "availability/update-from-to/",
        update_from_to_hotel_availability,
        name="update_from_to_villa_availability",
    ),
] + router.urls

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
