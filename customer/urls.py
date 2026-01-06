from django.urls import path

from .views import *

from django.conf import settings
from django.conf.urls.static import static


from rest_framework.routers import SimpleRouter

router = SimpleRouter()
# Removed villa-bookings from router - now using custom path below

router.register("tickets", SupportTicketViewSet, basename="tickets")
router.register("ticket-messages", TicketMessageViewSet, basename="ticket-messages")

router.register(r"favourite-villas", FavouriteVillaViewSet, basename="favouritevilla")
router.register(r"villa-reviews", VillaReviewViewSet, basename="villa-review")

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
    # Villa/Resort/Couple Stay Bookings
    path(
        "villa-resort-and-couple-stay/bookings/",
        VillaBookingViewSet.as_view({"get": "list", "post": "create"}),
        name="villa-resort-couple-stay-booking-list",
    ),
    path(
        "villa-resort-and-couple-stay/bookings/<int:pk>/",
        VillaBookingViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
        name="villa-resort-couple-stay-booking-detail",
    ),
    path("villas/", VillaListAPIView.as_view(), name="villa-list"),
    path("villas/<int:villa_id>/", VillaDetailAPIView.as_view(), name="villa-detail"),
    path(
        "resort-and-couple-stay/<int:villa_id>/rooms/",
        VillaRoomListAPIView.as_view(),
        name="villa-room-list",
    ),
    path("room/<int:room_id>/", VillaRoomDetailAPIView.as_view(), name="room-detail"),
    path("available-rooms/", AvailableRoomsAPIView.as_view(), name="available-rooms"),
    path(
        "available-villa-resort-and-couple-stay/",
        AvailableVillasAPIView.as_view(),
        name="available-villa-resort-and-couple-stay",
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
    path(
        "villa-reviews/create/",
        VillaReviewCreateAPIView.as_view(),
        name="villa-review-create",
    ),
    path(
        "villas/<int:villa_id>/reviews/",
        VillaReviewListAPIView.as_view(),
        name="villa-reviews-list",
    ),
] + router.urls

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
