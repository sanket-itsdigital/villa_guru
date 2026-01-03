from django.shortcuts import get_object_or_404, render

# Create your views here.


from rest_framework import viewsets
from .models import VillaBooking
from .serializers import VillaBookingSerializer

from datetime import timedelta, date
from rest_framework.exceptions import ValidationError
from django.db import transaction
from decimal import Decimal

import uuid

import razorpay
from django.conf import settings
from rest_framework.response import Response
from hotel.models import villa, villa_rooms, VillaAvailability
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status


class VillaBookingViewSet(viewsets.ModelViewSet):
    queryset = VillaBooking.objects.filter(payment_status="paid").order_by("-id")
    serializer_class = VillaBookingSerializer

    @swagger_auto_schema(
        operation_description="Create a new villa booking. Creates a Razorpay order for payment.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=[
                "villa",
                "check_in",
                "check_out",
                "guest_count",
                "phone_number",
                "email",
            ],
            properties={
                "villa": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="Villa ID to book", example=1
                ),
                "check_in": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATE,
                    description="Check-in date (YYYY-MM-DD)",
                    example="2025-01-15",
                ),
                "check_out": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATE,
                    description="Check-out date (YYYY-MM-DD)",
                    example="2025-01-17",
                ),
                "guest_count": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="Number of guests", example=4
                ),
                "child_count": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Number of children",
                    example=0,
                    default=0,
                ),
                "is_for_self": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="Is booking for self",
                    example=True,
                    default=True,
                ),
                "first_name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Guest first name",
                    example="John",
                ),
                "last_name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Guest last name",
                    example="Doe",
                ),
                "phone_number": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Contact phone number",
                    example="+919876543210",
                ),
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description="Contact email address",
                    example="john.doe@example.com",
                ),
                "special_request": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Special requests or notes",
                    example="Late check-in requested",
                ),
                "payment_type": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=["cash", "online"],
                    description="Payment type",
                    example="online",
                    default="online",
                ),
            },
        ),
        responses={
            201: openapi.Response(
                description="Booking created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                        "booking_id": openapi.Schema(
                            type=openapi.TYPE_STRING, example="RS-BK0001"
                        ),
                        "villa": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                        "villa_details": openapi.Schema(
                            type=openapi.TYPE_OBJECT, description="Full villa details"
                        ),
                        "check_in": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            format=openapi.FORMAT_DATE,
                            example="2025-01-15",
                        ),
                        "check_out": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            format=openapi.FORMAT_DATE,
                            example="2025-01-17",
                        ),
                        "guest_count": openapi.Schema(
                            type=openapi.TYPE_INTEGER, example=4
                        ),
                        "child_count": openapi.Schema(
                            type=openapi.TYPE_INTEGER, example=0
                        ),
                        "first_name": openapi.Schema(
                            type=openapi.TYPE_STRING, example="John"
                        ),
                        "last_name": openapi.Schema(
                            type=openapi.TYPE_STRING, example="Doe"
                        ),
                        "phone_number": openapi.Schema(
                            type=openapi.TYPE_STRING, example="+919876543210"
                        ),
                        "email": openapi.Schema(
                            type=openapi.TYPE_STRING, example="john.doe@example.com"
                        ),
                        "base_amount": openapi.Schema(
                            type=openapi.TYPE_NUMBER, example=40000.00
                        ),
                        "gst_amount": openapi.Schema(
                            type=openapi.TYPE_NUMBER, example=4800.00
                        ),
                        "total_amount": openapi.Schema(
                            type=openapi.TYPE_NUMBER, example=44800.00
                        ),
                        "payment_status": openapi.Schema(
                            type=openapi.TYPE_STRING, example="pending"
                        ),
                        "order_id": openapi.Schema(
                            type=openapi.TYPE_STRING, example="order_abc123"
                        ),
                        "status": openapi.Schema(
                            type=openapi.TYPE_STRING, example="confirmed"
                        ),
                        "created_at": openapi.Schema(
                            type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME
                        ),
                    },
                ),
            ),
            400: openapi.Response(description="Bad request - Validation error"),
            401: openapi.Response(description="Unauthorized - Authentication required"),
        },
        tags=["Bookings"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="List all bookings for the authenticated user",
        responses={
            200: openapi.Response(
                description="List of bookings",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_OBJECT),
                ),
            ),
            401: openapi.Response(description="Unauthorized"),
        },
        tags=["Bookings"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve a specific booking by ID",
        responses={
            200: openapi.Response(
                description="Booking details",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT),
            ),
            404: openapi.Response(description="Booking not found"),
            401: openapi.Response(description="Unauthorized"),
        },
        tags=["Bookings"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def perform_create(self, serializer):
        request_id = uuid.uuid4()
        print(f"🚨 perform_create() called for booking — ID: {request_id}")

        with transaction.atomic():
            booking = serializer.save(user=self.request.user)
            print(f"➡️  Booking saved: {booking.pk}, Villa: {booking.villa.name}")

            # Villa-level booking: whole villa is booked
            print(f"✅ Villa-level booking: {booking.villa.name} booked as whole villa")

            # --- ✅ Create Razorpay order here ---
            client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )

            amount = booking.total_amount  # use your booking amount
            order_data = {
                "amount": int(amount * 100),  # in paise
                "currency": "INR",
                "receipt": f"booking_{booking.id}",
                "payment_capture": 1,  # 👈 auto capture payment
                "notes": {  # 👈 custom metadata
                    "booking_id": str(booking.id),
                    "user_id": str(self.request.user.id),
                },
            }

            order = client.order.create(order_data)

            # Save order_id in booking
            booking.order_id = order["id"]
            booking.save()
            print(f"✅ Razorpay order created: {order['id']} for booking {booking.id}")

    def get_queryset(self):
        return VillaBooking.objects.filter(
            payment_status__in=["paid", "pending"], user=self.request.user
        ).order_by("-id")


from rest_framework.views import APIView


class VillaBookingRecalculateAPIView(APIView):
    def post(self, request):
        try:
            room_id = request.data.get("room_id")
            hotel_id = request.data.get("hotel_id")
            check_in = request.data.get("check_in")
            check_out = request.data.get("check_out")
            no_of_rooms = int(request.data.get("no_of_rooms", 1))

            if not check_in or not check_out:
                return Response(
                    {"error": "check_in and check_out are required"}, status=400
                )

            # Determine pricing: room-based or villa-based
            if room_id:
                # Room-based pricing (legacy)
                room = villa_rooms.objects.get(id=room_id)
                price_per_night = room.price_per_night
                nights = (
                    date.fromisoformat(check_out) - date.fromisoformat(check_in)
                ).days or 1
                base = price_per_night * nights * no_of_rooms
            elif hotel_id:
                # Villa-based pricing (whole villa)
                villa_obj = villa.objects.get(id=hotel_id)
                if not villa_obj.price_per_night:
                    return Response(
                        {"error": "Villa does not have a price set"}, status=400
                    )
                # Use marked-up price for customer display
                price_per_night = (
                    villa_obj.get_marked_up_price() or villa_obj.price_per_night
                )
                nights = (
                    date.fromisoformat(check_out) - date.fromisoformat(check_in)
                ).days or 1
                base = price_per_night * nights  # Whole villa, no_of_rooms not used
            else:
                return Response(
                    {"error": "Either room_id or hotel_id is required"}, status=400
                )

            gst_percent = Decimal("0.05") if price_per_night < 7500 else Decimal("0.12")
            gst = base * gst_percent
            subtotal = base + gst

            tcs = base * Decimal("0.005")
            tds = base * Decimal("0.001")

            return Response(
                {
                    "nights": nights,
                    "price_per_night": price_per_night,
                    "base_amount": base,
                    "gst_amount": gst,
                    "total_amount": subtotal,
                    "tds_amount": tds,
                    "tcs_amount": tcs,
                }
            )

        except Exception as e:
            return Response({"error": str(e)}, status=400)


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from hotel.models import villa
from hotel.filters import *
from .serializers import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from hotel.models import villa, villa_rooms
from .filters import VillaRoomFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


@csrf_exempt
def cancelltation_policy(request):

    return render(request, "cancelltation_policy.html")


@csrf_exempt
def guest_policy(request):

    return render(request, "guest_policy.html")


@csrf_exempt
def privacy_policy(request):

    return render(request, "privacy_policy.html")


@csrf_exempt
def terms_condition(request):

    return render(request, "terms_condition.html")


class VillaListAPIView(generics.ListAPIView):
    serializer_class = VillaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = VillaFilter

    def get_queryset(self):
        return villa.objects.annotate(room_count=Count("rooms")).filter(
            go_live=True, is_active=True, room_count__gt=0
        )

    def get_filterset_kwargs(self):
        kwargs = super().get_filterset_kwargs()
        kwargs["request"] = self.request
        return kwargs


class VillaDetailAPIView(generics.RetrieveAPIView):
    queryset = villa.objects.all().order_by("-id")
    serializer_class = VillaSerializer  # this one includes rooms and images
    lookup_url_kwarg = "villa_id"
    lookup_field = "id"


class VillaRoomListAPIView(generics.ListAPIView):
    serializer_class = VillaRoomSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = VillaRoomFilter

    def get_queryset(self):
        hotel_id = self.kwargs.get("hotel_id")
        return villa_rooms.objects.filter(villa_id=hotel_id)


class VillaRoomDetailAPIView(generics.RetrieveAPIView):
    queryset = villa_rooms.objects.all().order_by("-id")
    serializer_class = VillaRoomSerializer
    lookup_url_kwarg = "room_id"  # matches your URL param


from rest_framework import generics
from rest_framework.exceptions import ValidationError
from django.db.models import Count
from datetime import datetime


class AvailableRoomsAPIView(generics.ListAPIView):
    serializer_class = VillaRoomSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = VillaRoomFilter

    def get_queryset(self):
        from_date_str = self.request.query_params.get("from_date")
        to_date_str = self.request.query_params.get("to_date")
        hotel_id = self.request.query_params.get("hotel_id")

        if not hotel_id:
            raise ValidationError("'hotel_id' is required.")

        if not from_date_str or not to_date_str:
            raise ValidationError("Both 'from_date' and 'to_date' are required.")

        from datetime import datetime

        try:
            from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
            to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError("Invalid date format. Use YYYY-MM-DD.")

        if to_date < from_date:
            raise ValidationError("'to_date' must be after 'from_date'.")

        total_days = (to_date - from_date).days + 1

        # ✅ Only check availability for rooms of the given hotel
        availability_qs = RoomAvailability.objects.filter(
            room__hotel_id=hotel_id,
            room__hotel__go_live=True,
            date__gte=from_date,
            date__lte=to_date,
            available_count__gt=0,
        )

        available_room_ids = (
            availability_qs.values("room")
            .annotate(available_days=Count("date", distinct=True))
            .filter(available_days=total_days)
            .values_list("room", flat=True)
        )

        qs = villa_rooms.objects.filter(id__in=available_room_ids)

        # Apply other filters
        filterset = VillaRoomFilter(self.request.GET, queryset=qs)
        return filterset.qs


class AvailableVillasAPIView(APIView):
    def get(self, request):
        city = request.query_params.get("city")
        check_in = request.query_params.get("check_in")
        check_out = request.query_params.get("check_out")

        if not city or not check_in or not check_out:
            return Response(
                {"error": "city, check_in, and check_out are required."}, status=400
            )

        try:
            check_in = datetime.strptime(check_in, "%Y-%m-%d").date()
            check_out = datetime.strptime(check_out, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."}, status=400
            )

        if check_in >= check_out:
            return Response({"error": "check_out must be after check_in"}, status=400)

        if check_in < date.today():
            return Response({"error": "check_in cannot be in the past."}, status=400)

        # Step 1: Get all villas in the given city that are active and go_live
        villas = villa.objects.filter(city_id=city, is_active=True, go_live=True)

        # Step 2: Calculate required dates for the booking period
        days = (check_out - check_in).days
        required_dates = {check_in + timedelta(days=i) for i in range(days)}

        # Step 3: Get all villa availabilities for the date range
        availabilities = VillaAvailability.objects.filter(
            villa__in=villas, date__gte=check_in, date__lt=check_out
        ).select_related("villa")

        # Step 4: Get all bookings for the date range to check conflicts
        from .models import VillaBooking

        conflicting_bookings = VillaBooking.objects.filter(
            villa__in=villas,
            check_in__lt=check_out,
            check_out__gt=check_in,
            status__in=["confirmed", "checked_in"],
        ).values_list("villa_id", "check_in", "check_out")

        # Step 5: Build villa → blocked_dates mapping from bookings
        from collections import defaultdict

        villa_blocked_dates = defaultdict(set)
        for villa_id, booking_check_in, booking_check_out in conflicting_bookings:
            # Calculate all dates in the booking range
            booking_dates = {
                booking_check_in + timedelta(days=i)
                for i in range((booking_check_out - booking_check_in).days)
            }
            villa_blocked_dates[villa_id].update(booking_dates)

        # Step 6: Build villa → closed_dates mapping from availability records
        villa_closed_dates = defaultdict(set)
        for availability in availabilities:
            if not availability.is_open:
                villa_closed_dates[availability.villa_id].add(availability.date)

        # Step 7: Filter villas that are available for all required dates
        available_villa_ids = []
        for villa_obj in villas:
            blocked_dates = villa_blocked_dates.get(villa_obj.id, set())
            closed_dates = villa_closed_dates.get(villa_obj.id, set())

            # A villa is available if:
            # 1. None of the required dates are blocked by bookings
            # 2. None of the required dates are marked as closed (is_open=False)
            if not (required_dates & blocked_dates) and not (
                required_dates & closed_dates
            ):
                available_villa_ids.append(villa_obj.id)

        # Step 6: Get available villas
        available_villas = villa.objects.filter(id__in=available_villa_ids).distinct()

        return Response(VillaSerializer(available_villas, many=True).data)


class TopPicksByGuestsAPIView(APIView):
    """
    API to get top 10 villas based on booking count.
    Returns villas that have the most bookings (confirmed/paid bookings only).
    """

    permission_classes = []  # Public API, no authentication required

    @swagger_auto_schema(
        operation_description="Get top 10 villas based on booking count (Top Picks By Guests)",
        responses={
            200: openapi.Response(
                description="List of top 10 villas with booking counts",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_OBJECT),
                ),
            ),
        },
        tags=["Villas"],
    )
    def get(self, request):
        from django.db.models import Count, Q
        from .serializers import VillaSerializer

        # Count bookings per villa (only confirmed/paid bookings, exclude cancelled)
        # Use 'villabooking' as the reverse relation name
        top_villas = (
            villa.objects.filter(is_active=True, go_live=True)
            .annotate(
                booking_count=Count(
                    "villabooking",
                    filter=Q(
                        villabooking__status__in=[
                            "confirmed",
                            "checked_in",
                            "completed",
                        ],
                        villabooking__payment_status__in=["paid"],
                    ),
                    distinct=True,
                )
            )
            .filter(booking_count__gt=0)  # Only villas with at least 1 booking
            .order_by("-booking_count")[:10]  # Order by booking count descending
        )  # Get top 10

        # Serialize the results
        serializer = VillaSerializer(
            top_villas, many=True, context={"request": request}
        )

        # Add booking_count to each villa in the response
        response_data = []
        for villa_obj, serialized_data in zip(top_villas, serializer.data):
            villa_data = dict(serialized_data)
            villa_data["booking_count"] = villa_obj.booking_count
            response_data.append(villa_data)

        return Response(response_data, status=200)


from datetime import datetime, time, timedelta


class CancelBookingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        try:
            booking = VillaBooking.objects.get(id=booking_id, user=request.user)
        except VillaBooking.DoesNotExist:
            return Response({"error": "Booking not found or unauthorized"}, status=404)

        if booking.status == "cancelled":
            return Response({"message": "Booking already cancelled"}, status=400)

        checkin_datetime = datetime.combine(booking.check_in, time(hour=9, minute=0))
        now = datetime.now()

        if now > checkin_datetime - timedelta(hours=24):
            return Response(
                {"error": "Cannot cancel less than 24 hours before check-in (9 AM)"},
                status=400,
            )

        # ✅ Restore room availability manually
        current_date = booking.check_in
        while current_date < booking.check_out:
            avail, _ = RoomAvailability.objects.get_or_create(
                room=booking.room, date=current_date
            )
            avail.available_count += booking.no_of_rooms
            avail.save()
            current_date += timedelta(days=1)

        booking.status = "cancelled"
        booking.save()

        return Response(
            {"message": "Booking cancelled and availability restored successfully"},
            status=200,
        )


from rest_framework import viewsets, permissions


class SupportTicketViewSet(viewsets.ModelViewSet):
    serializer_class = SupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SupportTicket.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


from rest_framework import status


class TicketMessageViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        ticket_id = request.query_params.get("ticket_id")
        if not ticket_id:
            return Response({"error": "ticket_id is required"}, status=400)

        messages = TicketMessage.objects.filter(ticket__id=ticket_id).order_by(
            "created_at"
        )
        serializer = TicketMessageSerializer(
            messages, many=True, context={"request": request}
        )
        return Response(serializer.data)

    def create(self, request):
        ticket_id = request.data.get("ticket")
        message = request.data.get("message")

        if not ticket_id or not message:
            return Response({"error": "ticket and message are required"}, status=400)

        ticket = get_object_or_404(SupportTicket, id=ticket_id)

        new_message = TicketMessage.objects.create(
            ticket=ticket, sender=request.user, message=message
        )

        serializer = TicketMessageSerializer(new_message, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FavouriteVillaViewSet(viewsets.ModelViewSet):
    queryset = favouritevilla.objects.all().order_by("-id")
    serializer_class = FavouriteVillaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        villa_obj = serializer.validated_data["villa"]

        if favouritevilla.objects.filter(user=user, villa=villa_obj).exists():
            raise ValidationError("You have already added this villa to favourites.")

        serializer.save(user=user)

    def get_queryset(self):
        # Optionally filter by current user
        if self.request.user.is_authenticated:
            return favouritevilla.objects.filter(user=self.request.user)
        return favouritevilla.objects.none()


import json
import logging
import razorpay
from django.conf import settings
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import VillaBooking, PaymentTransaction

logger = logging.getLogger(__name__)

from django.utils import timezone

from django.core.mail import send_mail
from django.conf import settings
import traceback

import json
import traceback
import logging
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import razorpay
from .models import VillaBooking, PaymentTransaction

# ✅ Custom logger (defined in settings.LOGGING)
logger = logging.getLogger("razorpay_webhook")


@api_view(["POST"])
@permission_classes([AllowAny])
def razorpay_booking_webhook(request):
    webhook_body = request.body.decode("utf-8")
    received_sig = request.headers.get("X-Razorpay-Signature")

    # Log the raw request and headers
    logger.info("🔔 Razorpay webhook triggered")
    logger.debug(f"Headers: {dict(request.headers)}")
    logger.debug(f"Body: {webhook_body}")

    debug_logs = []

    def log(msg):
        """Unified logging function"""
        logger.info(msg)
        debug_logs.append(str(msg))

    try:
        # ✅ Check webhook secret
        if not settings.RAZORPAY_WEBHOOK_SECRET:
            log("❌ Webhook secret missing in settings")
            return Response({"error": "Webhook secret not configured"}, status=500)

        # ✅ Verify signature
        try:
            client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )
            client.utility.verify_webhook_signature(
                webhook_body, received_sig, settings.RAZORPAY_WEBHOOK_SECRET
            )
        except razorpay.errors.SignatureVerificationError:
            log("⚠️ Invalid Razorpay webhook signature")
            logger.warning(
                f"Invalid signature. Headers={dict(request.headers)}, Body={webhook_body}"
            )
            send_mail(
                subject="⚠️ Razorpay Webhook: Invalid Signature",
                message=f"Invalid signature received.\n\nHeaders:\n{request.headers}\n\nBody:\n{webhook_body}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=["pratikgosavi654@gmail.com"],
                fail_silently=True,
            )
            return Response({"error": "Invalid signature"}, status=400)

        # ✅ Parse event
        event = json.loads(webhook_body)
        event_type = event.get("event")
        log(f"📢 Event received: {event_type}")

        if event_type not in [
            "payment.captured",
            "payment.authorized",
            "payment.failed",
            "payment.refunded",
        ]:
            log(f"Ignored event: {event_type}")
            return Response({"status": "ignored", "event": event_type})

        payment_entity = event.get("payload", {}).get("payment", {}).get("entity", {})
        order_id = payment_entity.get("order_id")
        payment_id = payment_entity.get("id")
        amount_paise = payment_entity.get("amount")
        amount = (amount_paise / 100) if amount_paise else 0
        currency = payment_entity.get("currency", "INR")
        status = payment_entity.get("status")

        notes = payment_entity.get("notes", {}) or {}
        booking_id = notes.get("booking_id")

        log(f"📌 Notes: {notes}")
        log(f"💳 Payment status: {status}")

        if not booking_id:
            log("❌ Booking ID missing in Razorpay notes")
            return Response({"error": "Booking ID missing"}, status=400)

        try:
            booking = VillaBooking.objects.get(id=booking_id)
        except VillaBooking.DoesNotExist:
            log(f"❌ VillaBooking {booking_id} not found")
            return Response({"error": "Booking not found"}, status=404)

        status_map = {
            "captured": "paid",
            "authorized": "pending",
            "failed": "failed",
            "created": "pending",
            "refunded": "refunded",
        }
        mapped_status = status_map.get(status, "pending")

        # ✅ Atomic update
        # ✅ Atomic update
        with transaction.atomic():
            # Only update if current booking not already paid
            if booking.payment_status != "paid" or mapped_status == "paid":
                booking.payment_id = payment_id
                booking.order_id = order_id
                booking.payment_status = mapped_status
                booking.payment_type = "online"
                if mapped_status == "paid":
                    booking.paid_at = timezone.now()
                booking.save()

            txn, created = PaymentTransaction.objects.get_or_create(
                booking=booking,
                razorpay_payment_id=payment_id,
                defaults={
                    "razorpay_order_id": order_id,
                    "amount": amount,
                    "currency": currency,
                    "status": mapped_status,
                    "response_payload": event,
                },
            )
            if not created:
                txn.status = mapped_status
                txn.response_payload = event
                txn.save()

        log(f"✅ Webhook processed successfully for Booking {booking_id}")

        # ✅ Email notification
        send_mail(
            subject=f"🧾 Razorpay Webhook Triggered — {event_type}",
            message=f"Razorpay webhook triggered.\n\n"
            f"Event: {event_type}\nBooking ID: {booking_id}\nPayment ID: {payment_id}\n"
            f"Order ID: {order_id}\nAmount: ₹{amount}\nStatus: {status}\nMapped: {mapped_status}\n\n"
            f"Logs:\n" + "\n".join(debug_logs) + "\n\n"
            f"Raw Payload:\n{webhook_body}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=["pratikgosavi654@gmail.com"],
            fail_silently=True,
        )

        return Response({"status": "ok"})

    except Exception as e:
        err_trace = traceback.format_exc()
        logger.exception(f"❌ Razorpay Webhook Error: {e}")
        send_mail(
            subject="❌ Razorpay Webhook Error",
            message=f"Error occurred:\n{str(e)}\n\nTraceback:\n{err_trace}\n\nBody:\n{webhook_body}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=["pratikgosavi654@gmail.com"],
            fail_silently=True,
        )
        return Response({"error": str(e)}, status=500)
