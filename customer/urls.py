from django.urls import path

from .views import *

from django.conf import settings
from django.conf.urls.static import static


from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register(r"villa-bookings", VillaBookingViewSet, basename="sdfdssdsa")

router.register("tickets", SupportTicketViewSet, basename="tickets")
router.register("ticket-messages", TicketMessageViewSet, basename="ticket-messages")

router.register(r"favourite-villas", FavouriteVillaViewSet, basename="favouritevilla")

urlpatterns = [
    path("cancelltation-policy/", cancelltation_policy, name="cancelltation_policy"),
    path("guest-policy/", guest_policy, name="guest_policy"),
    path("privacy-policy/", privacy_policy, name="privacy_policy"),
    path("terms-condition/", terms_condition, name="terms_condition"),
    path(
        "villa-prebooking-bookings/",
        VillaBookingRecalculateAPIView.as_view(),
        name="VillaBookingRecalculateAPIView",
    ),
    path("villas/", VillaListAPIView.as_view(), name="villa-list"),
    path("villas/<int:villa_id>/", VillaDetailAPIView.as_view(), name="villa-detail"),
    path(
        "villas/<int:villa_id>/rooms/",
        VillaRoomListAPIView.as_view(),
        name="villa-room-list",
    ),
    path("room/<int:room_id>/", VillaRoomDetailAPIView.as_view(), name="room-detail"),
    path("available-rooms/", AvailableRoomsAPIView.as_view(), name="available-rooms"),
    path(
        "available-villas/", AvailableVillasAPIView.as_view(), name="available-villas"
    ),
    path(
        "top-picks-by-guests/",
        TopPicksByGuestsAPIView.as_view(),
        name="top-picks-by-guests",
    ),
    path(
        "cancel-booking/<int:booking_id>/",
        CancelBookingAPIView.as_view(),
        name="cancel_booking",
    ),
    path("booking/webhook/", razorpay_booking_webhook, name="razorpay_booking_webhook"),
] + router.urls

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
