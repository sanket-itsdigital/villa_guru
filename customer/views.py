from django.shortcuts import get_object_or_404, render

# Create your views here.


from rest_framework import viewsets, generics, permissions
from .models import VillaBooking
from .serializers import VillaBookingSerializer

from datetime import timedelta, date, datetime
from rest_framework.exceptions import ValidationError
from django.db import transaction
from decimal import Decimal

import uuid

import razorpay
from django.conf import settings
from rest_framework.response import Response
from hotel.models import villa, villa_rooms, VillaAvailability, RoomAvailability
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
                "rooms": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description="List of rooms to book (required for Resort/Couple Stay, optional for Villa). Format: [{'room_id': 1, 'quantity': 2}, ...]",
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "room_id": openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description="Room ID",
                                example=1,
                            ),
                            "quantity": openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description="Number of rooms",
                                example=2,
                                default=1,
                            ),
                        },
                    ),
                    example=[{"room_id": 1, "quantity": 2}],
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

            # Log booking type
            if booking.booking_type == "whole_villa":
                print(
                    f"✅ Whole villa booking: {booking.villa.name} - all rooms booked automatically"
                )
            else:
                rooms_count = booking.booked_rooms.count()
                print(
                    f"✅ Room-based booking: {booking.villa.name} - {rooms_count} room(s) selected"
                )

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
                    "booking_type": booking.booking_type,
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


class CalculatePriceWithCouponAPIView(APIView):
    """
    Calculate booking price with weekend pricing and coupon support.
    Supports both villa (whole villa) and room-based (multiple rooms) bookings.
    """

    @swagger_auto_schema(
        operation_description="Calculate booking price with weekend pricing and coupon discount. "
        "villa_id is always required. For Villa property type, rooms are not needed (whole villa booking). "
        "For Resort and Couple Stay property types, rooms array is required.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["villa_id", "check_in", "check_out"],
            properties={
                "villa_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Villa ID (required). Property type determines if rooms are needed.",
                ),
                "rooms": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "room_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "quantity": openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                default=1,
                                description="Optional, defaults to 1",
                            ),
                        },
                    ),
                    description='Required for Resort and Couple Stay properties. Optional for Villa properties. Format: [{"room_id": 1}, {"room_id": 2}] or [{"room_id": 1, "quantity": 2}]',
                ),
                "check_in": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATE,
                    description="Check-in date (YYYY-MM-DD)",
                ),
                "check_out": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATE,
                    description="Check-out date (YYYY-MM-DD)",
                ),
                "coupon_code": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Optional coupon code to apply",
                ),
            },
        ),
        responses={
            200: openapi.Response(description="Price calculation successful"),
            400: openapi.Response(description="Invalid request or coupon"),
        },
        tags=["Bookings"],
    )
    def post(self, request):
        try:
            villa_id = request.data.get("villa_id")
            rooms = request.data.get("rooms", [])
            check_in_str = request.data.get("check_in")
            check_out_str = request.data.get("check_out")
            coupon_code = request.data.get("coupon_code", "").strip()

            # Validate villa_id is required
            if not villa_id:
                return Response(
                    {"error": "villa_id is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate dates
            if not check_in_str or not check_out_str:
                return Response(
                    {"error": "check_in and check_out dates are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
                check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if check_in >= check_out:
                return Response(
                    {"error": "check_out must be after check_in"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if check_in < date.today():
                return Response(
                    {"error": "check_in date cannot be in the past"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            nights = (check_out - check_in).days
            if nights == 0:
                nights = 1

            # Get villa and determine booking type based on property type
            try:
                villa_obj = villa.objects.get(id=villa_id)
            except villa.DoesNotExist:
                return Response(
                    {"error": "Villa not found"}, status=status.HTTP_404_NOT_FOUND
                )

            # Determine booking type based on property type
            property_type_name = None
            if villa_obj.property_type:
                property_type_name = villa_obj.property_type.name

            # Calculate base price
            total_base_amount = Decimal("0.00")
            booking_type = None

            # If property type is Villa, it's whole villa booking (rooms not needed)
            if property_type_name == "Villa":
                booking_type = "whole_villa"
                # Rooms are not required for Villa property type
            elif property_type_name in ["Resort", "Couple Stay"]:
                # For Resort and Couple Stay, rooms are required
                booking_type = "selected_rooms"
                if not rooms or not isinstance(rooms, list) or len(rooms) == 0:
                    return Response(
                        {
                            "error": "rooms array is required for Resort and Couple Stay properties"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Validate all rooms belong to this villa
                for room_data in rooms:
                    room_id = room_data.get("room_id")
                    if not room_id:
                        return Response(
                            {"error": "Each room object must have a room_id"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    try:
                        room = villa_rooms.objects.get(id=room_id, villa=villa_obj)
                    except villa_rooms.DoesNotExist:
                        return Response(
                            {
                                "error": f"Room with id {room_id} not found or does not belong to this villa"
                            },
                            status=status.HTTP_404_NOT_FOUND,
                        )
            else:
                return Response(
                    {
                        "error": "Invalid property type. Must be Villa, Resort, or Couple Stay"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Calculate daily prices (with weekend pricing applied per day)
            current_date = check_in
            while current_date < check_out:
                day_total = Decimal("0.00")

                if booking_type == "whole_villa":
                    # Get price for this specific date (includes weekend pricing)
                    price_for_date = villa_obj.get_marked_up_price(date=current_date)
                    if price_for_date:
                        day_total = price_for_date
                else:
                    # Room-based: calculate for each room
                    for room_data in rooms:
                        room_id = room_data.get("room_id")
                        quantity = int(
                            room_data.get("quantity", 1)
                        )  # Default to 1 if not specified

                        room = villa_rooms.objects.get(id=room_id, villa=villa_obj)

                        # Get date-specific pricing if exists
                        try:
                            room_pricing = RoomPricing.objects.get(
                                room=room, date=current_date
                            )
                            base_price = room_pricing.price_per_night
                        except RoomPricing.DoesNotExist:
                            base_price = room.price_per_night

                        # Apply weekend pricing if applicable
                        if villa_obj.weekend_percentage and current_date.weekday() in [
                            4,
                            5,
                            6,
                        ]:
                            weekend_multiplier = Decimal(1) + (
                                villa_obj.weekend_percentage / 100
                            )
                            price_per_night = base_price * weekend_multiplier
                        else:
                            price_per_night = base_price

                        room_day_total = price_per_night * quantity
                        day_total += room_day_total

                total_base_amount += day_total
                current_date += timedelta(days=1)

            # Calculate average price per night for GST calculation
            avg_price_per_night = (
                total_base_amount / nights if nights > 0 else Decimal("0.00")
            )

            # Calculate GST
            gst_percent = (
                Decimal("0.05") if avg_price_per_night < 7500 else Decimal("0.12")
            )
            gst_amount = total_base_amount * gst_percent

            # Subtotal before coupon
            subtotal_before_coupon = total_base_amount + gst_amount

            # Apply coupon if provided
            coupon_applied = False
            coupon_discount = Decimal("0.00")
            coupon_details = None
            final_total = subtotal_before_coupon

            if coupon_code:
                try:
                    coupon_obj = coupon.objects.get(
                        code=coupon_code.upper(), is_active=True
                    )

                    # Validate coupon dates
                    from django.utils import timezone

                    now = timezone.now()
                    if now < coupon_obj.start_date or now > coupon_obj.end_date:
                        return Response(
                            {
                                "error": "Coupon is not valid for current date",
                                "coupon_valid_from": coupon_obj.start_date.isoformat(),
                                "coupon_valid_until": coupon_obj.end_date.isoformat(),
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    # Check minimum purchase
                    if subtotal_before_coupon < coupon_obj.min_purchase:
                        return Response(
                            {
                                "error": f"Minimum purchase amount of ₹{coupon_obj.min_purchase} required for this coupon",
                                "minimum_purchase": float(coupon_obj.min_purchase),
                                "current_subtotal": float(subtotal_before_coupon),
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    # Calculate discount
                    if coupon_obj.type == "percent":
                        discount = subtotal_before_coupon * (
                            coupon_obj.discount_percentage / 100
                        )
                        if coupon_obj.max_discount:
                            discount = min(discount, coupon_obj.max_discount)
                    else:  # amount type
                        discount = coupon_obj.discount_amount

                    coupon_discount = discount
                    final_total = subtotal_before_coupon - coupon_discount
                    coupon_applied = True

                    coupon_details = {
                        "code": coupon_obj.code,
                        "title": coupon_obj.title,
                        "type": coupon_obj.type,
                        "discount_percentage": (
                            float(coupon_obj.discount_percentage)
                            if coupon_obj.discount_percentage
                            else None
                        ),
                        "discount_amount": (
                            float(coupon_obj.discount_amount)
                            if coupon_obj.discount_amount
                            else None
                        ),
                        "max_discount": (
                            float(coupon_obj.max_discount)
                            if coupon_obj.max_discount
                            else None
                        ),
                        "applied_discount": float(coupon_discount),
                    }

                except coupon.DoesNotExist:
                    return Response(
                        {"error": "Invalid or inactive coupon code"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Calculate other charges (for reference, not included in final_total)
            commission_percent = Decimal("0.10")
            commission = total_base_amount * commission_percent
            commission_gst_percent = Decimal("0.18")
            commission_gst = commission * commission_gst_percent
            tcs_percent = Decimal("0.005")
            tds_percent = Decimal("0.001")
            tcs_amount = total_base_amount * tcs_percent
            tds_amount = total_base_amount * tds_percent

            return Response(
                {
                    "booking_type": booking_type,
                    "villa_id": villa_obj.id if villa_obj else None,
                    "villa_name": villa_obj.name if villa_obj else None,
                    "check_in": check_in_str,
                    "check_out": check_out_str,
                    "nights": nights,
                    "price_summary": {
                        "base_amount": float(total_base_amount),
                        "gst_percentage": float(gst_percent * 100),
                        "gst_amount": float(gst_amount),
                        "subtotal_before_coupon": float(subtotal_before_coupon),
                        "coupon_applied": coupon_applied,
                        "coupon_discount": (
                            float(coupon_discount) if coupon_applied else 0.00
                        ),
                        "final_total": float(final_total),
                        "average_price_per_night": float(avg_price_per_night),
                    },
                    "coupon_details": coupon_details,
                    "breakdown": {
                        "base_amount": float(total_base_amount),
                        "gst_amount": float(gst_amount),
                        "subtotal": float(subtotal_before_coupon),
                        "discount": float(coupon_discount) if coupon_applied else 0.00,
                        "total": float(final_total),
                    },
                    "internal_calculation": {
                        "commission": float(commission),
                        "commission_gst": float(commission_gst),
                        "tcs_amount": float(tcs_amount),
                        "tds_amount": float(tds_amount),
                    },
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            import traceback

            return Response(
                {"error": str(e), "traceback": traceback.format_exc()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EventBookingCreateAPIView(APIView):
    """
    API for customers to book events by filling a form with their details.
    POST /customer/event-bookings/
    Body: {
        "event": 1,
        "name": "John Doe",
        "phone_number": "+919876543210",
        "email": "john@example.com",
        "number_of_people": 5
    }
    """

    permission_classes = []  # Allow public access (no authentication required)

    @swagger_auto_schema(
        operation_description="Create a new event booking. Customers can fill a form with their basic details.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["event", "name", "phone_number", "email", "number_of_people"],
            properties={
                "event": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Event ID to book",
                    example=1,
                ),
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Customer's full name",
                    example="John Doe",
                ),
                "phone_number": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Customer's phone number",
                    example="+919876543210",
                ),
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description="Customer's email address",
                    example="john@example.com",
                ),
                "number_of_people": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Number of people attending the event",
                    example=5,
                ),
            },
        ),
        responses={
            201: openapi.Response(
                description="Event booking created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "booking": openapi.Schema(type=openapi.TYPE_OBJECT),
                    },
                ),
            ),
            400: "Bad Request - Validation error",
            404: "Event not found",
        },
        tags=["Event Bookings"],
    )
    def post(self, request):
        from .models import EventBooking
        from masters.models import event

        event_id = request.data.get("event")
        name = request.data.get("name")
        phone_number = request.data.get("phone_number")
        email = request.data.get("email")
        number_of_people = request.data.get("number_of_people")

        # Validate required fields
        if not all([event_id, name, phone_number, email, number_of_people]):
            return Response(
                {
                    "success": False,
                    "message": "All fields are required: event, name, phone_number, email, number_of_people",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate number_of_people
        try:
            number_of_people = int(number_of_people)
            if number_of_people <= 0:
                return Response(
                    {
                        "success": False,
                        "message": "number_of_people must be greater than 0",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except (ValueError, TypeError):
            return Response(
                {
                    "success": False,
                    "message": "number_of_people must be a valid integer",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate event exists
        try:
            event_obj = event.objects.get(id=event_id)
        except event.DoesNotExist:
            return Response(
                {"success": False, "message": "Event not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Create booking
        booking = EventBooking.objects.create(
            event=event_obj,
            name=name,
            phone_number=phone_number,
            email=email,
            number_of_people=number_of_people,
            user=request.user if request.user.is_authenticated else None,
        )

        from .serializers import EventBookingSerializer

        serializer = EventBookingSerializer(booking)
        return Response(
            {
                "success": True,
                "message": "Event booking created successfully",
                "booking": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class EventBookingListAPIView(generics.ListAPIView):
    """
    API to list all event bookings (for admin dashboard).
    GET /customer/event-bookings/list/
    Requires authentication.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from .models import EventBooking

        return EventBooking.objects.all().order_by("-created_at")

    def get_serializer_class(self):
        from .serializers import EventBookingSerializer

        return EventBookingSerializer

    @swagger_auto_schema(
        operation_description="List all event bookings. Requires authentication.",
        responses={200: "List of event bookings"},
        tags=["Event Bookings"],
    )
    def get(self, request, *args, **kwargs):
        from .serializers import EventBookingSerializer

        # Only allow superusers to see all bookings
        if not request.user.is_superuser:
            return Response(
                {"error": "You do not have permission to view event bookings."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().get(request, *args, **kwargs)


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
        from datetime import datetime, timedelta, date
        from hotel.models import RoomAvailability
        from .models import VillaBooking
        from django.db.models import Count, Q

        # Base queryset: Only Resort and Couple Stay properties
        qs = villa.objects.annotate(room_count=Count("rooms")).filter(
            go_live=True,
            is_active=True,
            property_type__name__in=["Resort", "Couple Stay"],
            room_count__gt=0,
        )

        # Get query parameters
        check_in_str = self.request.query_params.get("check_in")
        check_out_str = self.request.query_params.get("check_out")
        city_id = self.request.query_params.get("city")

        # Filter by city if provided
        if city_id:
            try:
                qs = qs.filter(city_id=int(city_id))
            except (ValueError, TypeError):
                pass

        # If check_in and check_out are provided, filter by availability
        if check_in_str and check_out_str:
            try:
                check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
                check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()

                if check_in >= check_out:
                    return villa.objects.none()  # Invalid date range

                if check_in < date.today():
                    return villa.objects.none()  # Past date

                total_days = (check_out - check_in).days

                # Get all rooms for these resorts
                resort_rooms = villa_rooms.objects.filter(
                    villa__in=qs.values_list("id", flat=True)
                )

                # Get bookings that might block rooms
                conflicting_bookings = VillaBooking.objects.filter(
                    villa__in=qs.values_list("id", flat=True),
                    check_in__lt=check_out,
                    check_out__gt=check_in,
                    status__in=["confirmed", "checked_in"],
                    booking_type="selected_rooms",
                ).prefetch_related("booked_rooms")

                # Calculate booked quantities per room per date
                from collections import defaultdict

                room_booked_dates = defaultdict(lambda: defaultdict(int))

                for booking in conflicting_bookings:
                    for booked_room in booking.booked_rooms.all():
                        current_date = max(check_in, booking.check_in)
                        end_date = min(check_out, booking.check_out)
                        while current_date < end_date:
                            room_booked_dates[booked_room.room_id][
                                current_date
                            ] += booked_room.quantity
                            current_date += timedelta(days=1)

                # Check each room for availability across all dates
                # If RoomAvailability record doesn't exist, assume room is available (default behavior)
                truly_available_room_ids = []

                for room in resort_rooms:
                    is_available = True
                    current_date = check_in

                    while current_date < check_out:
                        # Use automatic calculation method - it handles everything
                        room_availability = RoomAvailability.get_or_calculate_availability(
                            room=room,
                            date=current_date
                        )
                        
                        # Check if manually closed
                        if room_availability.is_manually_closed:
                            is_available = False
                            break

                        # Get the calculated available count
                        available_count = room_availability.available_count

                        # Room is not available if available_count <= 0
                        if available_count <= 0:
                            is_available = False
                            break

                        current_date += timedelta(days=1)

                    if is_available:
                        truly_available_room_ids.append(room.id)

                # Get villas that have at least one available room
                if truly_available_room_ids:
                    available_villa_ids = (
                        villa_rooms.objects.filter(id__in=truly_available_room_ids)
                        .values_list("villa_id", flat=True)
                        .distinct()
                    )
                    qs = qs.filter(id__in=available_villa_ids)
                else:
                    # No rooms available for the date range, return empty queryset
                    qs = villa.objects.none()

            except (ValueError, TypeError):
                # Invalid date format, return empty queryset or all resorts
                pass

        return qs

    def get_filterset_kwargs(self):
        kwargs = super().get_filterset_kwargs()
        kwargs["request"] = self.request
        return kwargs


class VillaDetailAPIView(generics.RetrieveAPIView):
    queryset = villa.objects.all().order_by("-id")
    serializer_class = VillaSerializer  # this one includes rooms and images
    lookup_url_kwarg = "villa_id"
    lookup_field = "id"

    def get_serializer_context(self):
        """
        Add request to serializer context so is_like field can check user's favorites.
        """
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def retrieve(self, request, *args, **kwargs):
        """
        Override retrieve to remove rooms field and add room_types field.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        villa_data = serializer.data

        # Remove rooms field
        villa_data.pop("rooms", None)

        # Get room types for this property (only for Resort/Couple Stay)
        from masters.models import room_type
        from masters.serializers import room_type_serializer

        property_type_name = villa_data.get("property_type", {}).get("name", "")

        if property_type_name in ["Resort", "Couple Stay"]:
            # Get unique room types from this property's rooms
            room_types_qs = (
                room_type.objects.filter(rooms__villa=instance)
                .distinct()
                .prefetch_related("amenities", "rooms__images")
            )

            room_types_serializer = room_type_serializer(
                room_types_qs, many=True, context={"request": request}
            )
            villa_data["room_types"] = room_types_serializer.data
        else:
            # Villa properties don't have individual room types
            villa_data["room_types"] = []

        return Response(villa_data)


class VillaRoomListAPIView(generics.ListAPIView):
    """
    List all rooms for a specific villa.
    For Resort and Couple Stay properties, this shows all available rooms.
    For Villa properties, this will be empty as rooms are not individually bookable.
    """

    serializer_class = VillaRoomSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = VillaRoomFilter

    def get_queryset(self):
        villa_id = self.kwargs.get("villa_id")
        # Only show rooms for Resort and Couple Stay properties
        # Villa properties don't have individually bookable rooms
        return (
            villa_rooms.objects.filter(
                villa_id=villa_id,
                villa__property_type__name__in=["Resort", "Couple Stay"],
            )
            .select_related("villa", "room_type")
            .prefetch_related("villa_amenities", "images")
        )


class VillaRoomDetailAPIView(generics.RetrieveAPIView):
    queryset = villa_rooms.objects.all().order_by("-id")
    serializer_class = VillaRoomSerializer
    lookup_url_kwarg = "room_id"  # matches your URL param


class PropertyRoomTypesAPIView(APIView):
    """
    Get all room types for a specific property (Villa/Resort/Couple Stay).

    Query Parameters:
    - property_id (required): ID of the property (villa/resort/couple stay)

    Returns a list of unique room types used in that property's rooms.
    For Villa properties, returns empty list as villas don't have individual rooms.
    """

    def get(self, request):
        from hotel.models import villa, villa_rooms
        from masters.serializers import room_type_serializer
        from rest_framework.exceptions import ValidationError

        property_id = request.query_params.get("property_id")

        if not property_id:
            return Response(
                {"error": "property_id is required as query parameter."}, status=400
            )

        try:
            property_id = int(property_id)
        except ValueError:
            return Response(
                {"error": "property_id must be a valid integer."}, status=400
            )

        # Get the property
        try:
            property_obj = villa.objects.select_related("property_type").get(
                id=property_id
            )
        except villa.DoesNotExist:
            return Response(
                {"error": f"Property with id {property_id} not found."}, status=404
            )

        # Check property type
        property_type_name = (
            property_obj.property_type.name if property_obj.property_type else None
        )

        # Villa properties don't have individual room types
        if property_type_name == "Villa":
            return Response(
                {
                    "property_id": property_id,
                    "property_name": property_obj.name,
                    "property_type": property_type_name,
                    "message": "Villa properties are booked as whole units and do not have individual room types.",
                    "room_types": [],
                }
            )

        # For Resort and Couple Stay, get unique room types from their rooms
        if property_type_name in ["Resort", "Couple Stay"]:
            # Get all unique room types used in this property's rooms
            from masters.models import room_type

            room_types = (
                room_type.objects.filter(rooms__villa=property_obj)
                .distinct()
                .prefetch_related("amenities")
            )

            serializer = room_type_serializer(
                room_types, many=True, context={"request": request}
            )

            return Response(
                {
                    "property_id": property_id,
                    "property_name": property_obj.name,
                    "property_type": property_type_name,
                    "room_types_count": room_types.count(),
                    "room_types": serializer.data,
                }
            )

        # Unknown property type
        return Response(
            {
                "property_id": property_id,
                "property_name": property_obj.name,
                "property_type": property_type_name,
                "message": "Unknown property type.",
                "room_types": [],
            }
        )


from rest_framework import generics
from rest_framework.exceptions import ValidationError
from django.db.models import Count
from datetime import datetime
from masters.models import coupon
from hotel.models import RoomPricing


class AvailableRoomsAPIView(generics.ListAPIView):
    serializer_class = VillaRoomSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = VillaRoomFilter

    def get_queryset(self):
        from_date_str = self.request.query_params.get("from_date")
        to_date_str = self.request.query_params.get("to_date")
        villa_id = self.request.query_params.get("villa_id")

        if not villa_id:
            raise ValidationError("'villa_id' is required.")

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

        # Get all rooms for the given villa (Resort/Couple Stay only)
        rooms = villa_rooms.objects.filter(
            villa_id=villa_id,
            villa__go_live=True,
            villa__property_type__name__in=["Resort", "Couple Stay"],
        )

        if not rooms.exists():
            return villa_rooms.objects.none()

        # Get bookings that might block rooms
        from .models import VillaBooking
        from collections import defaultdict
        from datetime import timedelta

        conflicting_bookings = VillaBooking.objects.filter(
            villa_id=villa_id,
            check_in__lt=to_date + timedelta(days=1),  # Include to_date
            check_out__gt=from_date,
            status__in=["confirmed", "checked_in"],
            booking_type="selected_rooms",
        ).prefetch_related("booked_rooms")

        # Calculate booked quantities per room per date
        room_booked_dates = defaultdict(lambda: defaultdict(int))

        for booking in conflicting_bookings:
            for booked_room in booking.booked_rooms.all():
                current_date = max(from_date, booking.check_in)
                end_date = min(to_date + timedelta(days=1), booking.check_out)
                while current_date < end_date:
                    room_booked_dates[booked_room.room_id][
                        current_date
                    ] += booked_room.quantity
                    current_date += timedelta(days=1)

        # Check each room for availability across all dates
        # Now using room_count instead of RoomAvailability.available_count
        truly_available_room_ids = []
        room_availability_data = {}  # Store availability info for each room

        for room in rooms:
            is_available = True
            current_date = from_date
            min_available = float("inf")  # Track minimum available across all dates

            # Get total room count for this room type
            total_room_count = (
                room.room_count
                if hasattr(room, "room_count") and room.room_count
                else 1
            )

            while current_date < to_date:
                # Use automatic calculation method - it handles everything
                room_availability = RoomAvailability.get_or_calculate_availability(
                    room=room,
                    date=current_date
                )
                
                # Check if manually closed
                if room_availability.is_manually_closed:
                    is_available = False
                    min_available = 0
                    break

                # Get the calculated available count
                available_count = room_availability.available_count
                min_available = min(min_available, available_count)

                # Room is not available if available_count <= 0
                if available_count <= 0:
                    is_available = False
                    break

                current_date += timedelta(days=1)

            if is_available:
                truly_available_room_ids.append(room.id)
                # Store availability data for serializer
                room_availability_data[room.id] = {
                    "total_rooms": total_room_count,
                    "available_rooms": (
                        max(0, min_available)
                        if min_available != float("inf")
                        else total_room_count
                    ),
                    "booked_rooms": (
                        total_room_count - max(0, min_available)
                        if min_available != float("inf")
                        else 0
                    ),
                }

        qs = (
            villa_rooms.objects.filter(id__in=truly_available_room_ids)
            .select_related("room_type", "villa")
            .prefetch_related("villa_amenities", "images")
        )

        # Apply other filters
        filterset = VillaRoomFilter(self.request.GET, queryset=qs)
        filtered_qs = filterset.qs

        # Add availability data to each room object for serializer
        for room in filtered_qs:
            if room.id in room_availability_data:
                room.available_count = room_availability_data[room.id][
                    "available_rooms"
                ]
                room.total_rooms = room_availability_data[room.id]["total_rooms"]
                room.booked_count = room_availability_data[room.id]["booked_rooms"]

        return filtered_qs


class AvailableVillasAPIView(APIView):
    def get(self, request):
        city = request.query_params.get("city")
        check_in = request.query_params.get("check_in")
        check_out = request.query_params.get("check_out")
        property_type_id = request.query_params.get("property_type")

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

        # Step 1: Get all properties in the given city that are active and go_live
        villas = villa.objects.filter(city_id=city, is_active=True, go_live=True)

        # Filter by property_type if provided
        if property_type_id:
            try:
                villas = villas.filter(property_type_id=int(property_type_id))
            except (ValueError, TypeError):
                return Response({"error": "Invalid property_type ID."}, status=400)

        # Step 2: Calculate required dates for the booking period
        # Note: check_out date is the departure date, so we don't need availability for that day
        days = (check_out - check_in).days
        required_dates = {check_in + timedelta(days=i) for i in range(days)}

        # Step 3: Separate properties by type for different availability checks
        villa_properties = villas.filter(property_type__name="Villa")
        resort_couple_stay_properties = villas.filter(
            property_type__name__in=["Resort", "Couple Stay"]
        )

        # Get all villa availabilities for the date range (only for Villa properties)
        availabilities = VillaAvailability.objects.filter(
            villa__in=villa_properties, date__gte=check_in, date__lt=check_out
        ).select_related("villa")

        # Step 4: Get all bookings for the date range to check conflicts (only Villa whole_villa bookings)
        from .models import VillaBooking

        # Check for any bookings that overlap with the requested date range (both online and offline)
        # A booking overlaps if: booking.check_in < request.check_out AND booking.check_out > request.check_in
        conflicting_bookings = VillaBooking.objects.filter(
            villa__in=villa_properties,
            booking_type="whole_villa",  # Only whole villa bookings block Villa properties
            check_in__lt=check_out,  # Booking starts before requested check-out
            check_out__gt=check_in,  # Booking ends after requested check-in
            status__in=[
                "confirmed",
                "checked_in",
                "pending",
            ],  # Include pending bookings too (both online and offline)
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
        # Only mark dates as closed if VillaAvailability record exists AND is_open=False
        # If no record exists, assume villa is open (available)
        # Also check for offline bookings - they should block availability
        villa_closed_dates = defaultdict(set)
        for availability in availabilities:
            if not availability.is_open:
                villa_closed_dates[availability.villa_id].add(availability.date)

        # Also check for offline bookings - they close availability automatically
        offline_bookings = VillaBooking.objects.filter(
            villa__in=villa_properties,
            booking_type="whole_villa",
            payment_type="cash",  # Offline bookings
            check_in__lt=check_out,
            check_out__gt=check_in,
            status__in=["confirmed", "checked_in", "pending"],
        )

        for booking in offline_bookings:
            current_date = booking.check_in
            while current_date < booking.check_out:
                villa_closed_dates[booking.villa_id].add(current_date)
                current_date += timedelta(days=1)

        # Step 7: Filter properties that are available for all required dates
        # Property types already separated above
        available_villa_ids = []

        # Check Villa properties (whole villa booking)
        for villa_obj in villa_properties:
            blocked_dates = villa_blocked_dates.get(villa_obj.id, set())
            closed_dates = villa_closed_dates.get(villa_obj.id, set())

            # A villa is available if:
            # 1. None of the required dates are blocked by bookings
            # 2. None of the required dates are marked as closed (is_open=False in VillaAvailability)
            # Note: If no VillaAvailability record exists for a date, villa is considered open/available by default
            has_blocked = bool(required_dates & blocked_dates)
            has_closed = bool(required_dates & closed_dates)

            # Debug: Print availability check for troubleshooting
            # if has_blocked:
            #     print(f"Villa {villa_obj.id} ({villa_obj.name}) is blocked. Blocked dates: {sorted(blocked_dates)}")
            #     print(f"Required dates: {sorted(required_dates)}")
            #     print(f"Overlap: {sorted(required_dates & blocked_dates)}")

            # Villa is available if it's not blocked and not explicitly closed
            if not has_blocked and not has_closed:
                available_villa_ids.append(villa_obj.id)

        # Check Resort/Couple Stay properties (room-based booking)
        if resort_couple_stay_properties.exists():
            # Get all rooms for these resorts
            resort_rooms = villa_rooms.objects.filter(
                villa__in=resort_couple_stay_properties
            )

            # Get bookings that might block rooms (both online and offline)
            conflicting_bookings = VillaBooking.objects.filter(
                villa__in=resort_couple_stay_properties,
                check_in__lt=check_out,
                check_out__gt=check_in,
                status__in=["confirmed", "checked_in", "pending"],
                booking_type="selected_rooms",
            ).prefetch_related("booked_rooms")

            # Calculate booked quantities per room per date
            from collections import defaultdict

            room_booked_dates = defaultdict(lambda: defaultdict(int))

            for booking in conflicting_bookings:
                for booked_room in booking.booked_rooms.all():
                    current_date = max(check_in, booking.check_in)
                    end_date = min(check_out, booking.check_out)
                    while current_date < end_date:
                        room_booked_dates[booked_room.room_id][
                            current_date
                        ] += booked_room.quantity
                        current_date += timedelta(days=1)

            # Check each room for availability across all dates
            # Now using room_count instead of RoomAvailability
            truly_available_room_ids = []

            for room in resort_rooms:
                is_available = True
                current_date = check_in

                # Get total room count for this room type
                total_room_count = room.room_count if hasattr(room, "room_count") else 1

                while current_date < check_out:
                    # Use automatic calculation method - it handles everything
                    room_availability = RoomAvailability.get_or_calculate_availability(
                        room=room,
                        date=current_date
                    )
                    
                    # Check if manually closed
                    if room_availability.is_manually_closed:
                        is_available = False
                        break
                    
                    # Get the calculated available count
                    available_count = room_availability.available_count

                    # Room is not available if available_count <= 0
                    if available_count <= 0:
                        is_available = False
                        break

                    current_date += timedelta(days=1)

                if is_available:
                    truly_available_room_ids.append(room.id)

            # Get resorts that have at least one available room
            if truly_available_room_ids:
                available_resort_ids = (
                    villa_rooms.objects.filter(id__in=truly_available_room_ids)
                    .values_list("villa_id", flat=True)
                    .distinct()
                )
                available_villa_ids.extend(available_resort_ids)

        # Step 8: Add favorited villas and rooms to available list (even if not available)
        favorite_villa_ids = set(
            available_villa_ids
        )  # Convert to set for easier manipulation

        if request.user.is_authenticated:
            from .models import favouritevilla

            # Get user's favorites filtered by city and active status
            user_favorites_query = favouritevilla.objects.filter(
                user=request.user,
                villa__city_id=city,
                villa__is_active=True,
                villa__go_live=True,
            )

            # Filter by property_type if provided
            if property_type_id:
                user_favorites_query = user_favorites_query.filter(
                    villa__property_type_id=int(property_type_id)
                )

            # Get favorited villa IDs (whole villa favorites)
            favorited_villa_ids = user_favorites_query.filter(
                room__isnull=True
            ).values_list("villa_id", flat=True)

            # Add favorited villas to available list
            favorite_villa_ids.update(favorited_villa_ids)

            # Get favorited room IDs (Resort/Couple Stay room favorites)
            favorited_room_villa_ids = (
                user_favorites_query.filter(room__isnull=False)
                .values_list("villa_id", flat=True)
                .distinct()
            )

            # Add villas that have favorited rooms to available list
            favorite_villa_ids.update(favorited_room_villa_ids)

        # Step 9: Get available properties (including favorites)
        available_villas = (
            villa.objects.filter(id__in=favorite_villa_ids)
            .select_related("property_type", "city", "user")
            .prefetch_related("rooms__room_type", "rooms__room_type__amenities")
            .distinct()
            if favorite_villa_ids
            else villa.objects.none()
        )

        # Step 10: Apply Django filters (price range, villa_star_facility, amenities)
        from .filters import AvailableVillaFilter

        filterset = AvailableVillaFilter(request.GET, queryset=available_villas)
        filtered_villas = filterset.qs

        serializer = VillaSerializer(
            filtered_villas, many=True, context={"request": request}
        )

        # Get room types for each property and modify response
        from masters.models import room_type
        from masters.serializers import room_type_serializer

        # Create a mapping of villa_id to villa object for quick lookup
        villa_dict = {v.id: v for v in filtered_villas}

        response_data = []
        for villa_data in serializer.data:
            # Remove rooms field
            villa_data.pop("rooms", None)

            # Get room types for this property (only for Resort/Couple Stay)
            property_type_name = villa_data.get("property_type", {}).get("name", "")
            villa_id = villa_data.get("id")

            if property_type_name in ["Resort", "Couple Stay"]:
                # Get unique room types from this property's rooms
                villa_obj = villa_dict.get(villa_id)
                if villa_obj:
                    room_types_qs = (
                        room_type.objects.filter(rooms__villa=villa_obj)
                        .distinct()
                        .prefetch_related("amenities", "rooms__images")
                    )

                    room_types_serializer = room_type_serializer(
                        room_types_qs, many=True, context={"request": request}
                    )
                    villa_data["room_types"] = room_types_serializer.data
                else:
                    villa_data["room_types"] = []
            else:
                # Villa properties don't have individual room types
                villa_data["room_types"] = []

            response_data.append(villa_data)

        return Response(response_data)


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

        # Restore availability when booking is cancelled
        from hotel.models import VillaAvailability, RoomAvailability
        from customer.models import BookingRoom

        current_date = booking.check_in
        while current_date < booking.check_out:
            if booking.booking_type == "whole_villa":
                # Villa property: Restore availability (mark as open)
                VillaAvailability.objects.update_or_create(
                    villa=booking.villa,
                    date=current_date,
                    defaults={"is_open": True},  # Make available again
                )
            else:
                # Resort/Couple Stay: Restore room availability
                booked_rooms = BookingRoom.objects.filter(booking=booking)
                for booked_room in booked_rooms:
                    room_avail, created = RoomAvailability.objects.get_or_create(
                        room=booked_room.room,
                        date=current_date,
                        defaults={"available_count": 1},  # Default if not exists
                    )
                    # Restore the booked quantity
                    room_avail.available_count += booked_room.quantity
                    room_avail.save()

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
    """
    ViewSet to manage favorites for:
    - Whole villas (POST with villa_id only)
    - Resort/Couple Stay rooms (POST with villa_id and room_id)

    GET /customer/favourite-villas/ - List all favorites
    POST /customer/favourite-villas/ - Add favorite (villa or room)
    DELETE /customer/favourite-villas/{id}/ - Remove favorite
    """

    queryset = favouritevilla.objects.all().order_by("-id")
    serializer_class = FavouriteVillaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        villa_obj = serializer.validated_data.get("villa")
        room_obj = serializer.validated_data.get("room")

        # Check if already favorited
        if room_obj:
            # Room favorite - check unique combination
            if favouritevilla.objects.filter(
                user=user, villa=villa_obj, room=room_obj
            ).exists():
                raise ValidationError("You have already added this room to favourites.")
        else:
            # Villa favorite - check if villa is already favorited (without room)
            if favouritevilla.objects.filter(
                user=user, villa=villa_obj, room__isnull=True
            ).exists():
                raise ValidationError(
                    "You have already added this villa to favourites."
                )

        serializer.save(user=user)

    def get_queryset(self):
        # Filter by current user
        if self.request.user.is_authenticated:
            queryset = favouritevilla.objects.filter(user=self.request.user)

            # Optional filtering by type
            favorite_type = self.request.query_params.get("type")
            if favorite_type == "villa":
                queryset = queryset.filter(room__isnull=True)
            elif favorite_type == "room":
                queryset = queryset.filter(room__isnull=False)

            # Optional filtering by villa_id
            villa_id = self.request.query_params.get("villa_id")
            if villa_id:
                queryset = queryset.filter(villa_id=villa_id)

            return queryset.order_by("-id")
        return favouritevilla.objects.none()

    def get_object(self):
        """
        Override to look up by villa_id (from URL) and optional room_id (from query params)
        instead of using the favorite record primary key.
        """
        # Get villa_id from URL kwargs (the :id parameter)
        villa_id = self.kwargs.get("pk")
        if not villa_id:
            from rest_framework.exceptions import NotFound

            raise NotFound("villa_id is required in URL")

        # Get room_id from query params (optional)
        room_id = self.request.query_params.get("room_id")

        try:
            if room_id:
                # Get specific room favorite
                try:
                    room_id_int = int(room_id)
                except (ValueError, TypeError):
                    from rest_framework.exceptions import ValidationError

                    raise ValidationError("Invalid room_id")

                favorite = favouritevilla.objects.get(
                    user=self.request.user, villa_id=villa_id, room_id=room_id_int
                )
            else:
                # Get whole villa favorite (room is null)
                favorite = favouritevilla.objects.get(
                    user=self.request.user, villa_id=villa_id, room__isnull=True
                )

            return favorite
        except favouritevilla.DoesNotExist:
            from rest_framework.exceptions import NotFound

            if room_id:
                raise NotFound(
                    f"This room (ID: {room_id}) from villa (ID: {villa_id}) is not in your favorites."
                )
            else:
                raise NotFound(f"This villa (ID: {villa_id}) is not in your favorites.")

    def destroy(self, request, *args, **kwargs):
        """
        Delete a favorite by villa_id (in URL) and optional room_id (in query params).
        DELETE /customer/favourite-villas/{villa_id}/?room_id=5  - Remove specific room favorite
        DELETE /customer/favourite-villas/{villa_id}/           - Remove whole villa favorite
        """
        # Get the favorite object using our custom get_object
        instance = self.get_object()

        # Store info before deletion for the response
        is_room_favorite = instance.room is not None
        villa_id = instance.villa.id
        villa_name = instance.villa.name
        room_id = instance.room.id if instance.room else None
        room_title = instance.room.title if instance.room else None
        favorite_id = instance.id

        # Perform deletion
        self.perform_destroy(instance)

        # Return success message
        if is_room_favorite:
            message = f"Room '{room_title}' from '{villa_name}' has been removed from your favorites."
        else:
            message = f"Villa '{villa_name}' has been removed from your favorites."

        return Response(
            {
                "success": True,
                "message": message,
                "favorite_id": favorite_id,
                "villa_id": villa_id,
                "villa_name": villa_name,
                "room_id": room_id,
                "room_title": room_title,
                "favorite_type": "room" if is_room_favorite else "villa",
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        """
        Delete a favorite and return a proper success message.
        """
        instance = self.get_object()

        # Store info before deletion for the message
        is_room_favorite = instance.room is not None
        villa_name = instance.villa.name
        room_title = instance.room.title if instance.room else None
        favorite_id = instance.id

        # Perform deletion
        self.perform_destroy(instance)

        # Return success message
        if is_room_favorite:
            message = f"Room '{room_title}' from '{villa_name}' has been removed from your favorites."
        else:
            message = f"Villa '{villa_name}' has been removed from your favorites."

        return Response(
            {
                "success": True,
                "message": message,
                "favorite_id": favorite_id,
                "villa_id": instance.villa.id,
                "villa_name": villa_name,
                "room_id": instance.room.id if instance.room else None,
                "room_title": room_title,
                "favorite_type": "room" if is_room_favorite else "villa",
            },
            status=status.HTTP_200_OK,
        )


class VillaReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for villa reviews.
    Customers can create, update, and delete their own reviews.
    """

    serializer_class = VillaReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return reviews filtered by villa if villa_id is provided in query params.
        Otherwise, return all reviews for the current user.
        """
        queryset = VillaReview.objects.all()
        villa_id = self.request.query_params.get("villa_id")

        if villa_id:
            queryset = queryset.filter(villa_id=villa_id)

        # If user is not admin, only show their own reviews when listing all
        if not self.request.user.is_superuser:
            if not villa_id:
                queryset = queryset.filter(user=self.request.user)

        return queryset.order_by("-created_at")

    def perform_create(self, serializer):
        """
        Set the user to the current authenticated user.
        Ensure only customers can create reviews.
        """
        if not self.request.user.is_customer:
            raise ValidationError("Only customers can create reviews.")

        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """
        Ensure users can only update their own reviews.
        """
        if serializer.instance.user != self.request.user:
            raise ValidationError("You can only update your own reviews.")

        serializer.save()

    def perform_destroy(self, instance):
        """
        Ensure users can only delete their own reviews.
        """
        if instance.user != self.request.user and not self.request.user.is_superuser:
            raise ValidationError("You can only delete your own reviews.")

        instance.delete()


class VillaReviewCreateAPIView(generics.CreateAPIView):
    """
    Create a new review for a villa.
    POST /customer/villa-reviews/create/
    Only customers can create reviews.
    """

    serializer_class = VillaReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a new villa review. Only customers can create reviews.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["villa", "rating", "comment"],
            properties={
                "villa": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="Villa ID"
                ),
                "rating": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Rating from 1 to 5 stars",
                    enum=[1, 2, 3, 4, 5],
                ),
                "comment": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Review comment/feedback"
                ),
            },
        ),
        responses={
            201: VillaReviewSerializer,
            400: "Bad request - Validation error",
            403: "Forbidden - Only customers can create reviews",
        },
    )
    def post(self, request, *args, **kwargs):
        if not request.user.is_customer:
            return Response(
                {"error": "Only customers can create reviews."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Set the user to the current authenticated user."""
        serializer.save(user=self.request.user)


class VillaReviewListAPIView(generics.ListAPIView):
    """
    List all reviews for a specific villa.
    GET /customer/villas/{villa_id}/reviews/
    Public endpoint - no authentication required.
    """

    serializer_class = VillaReviewSerializer
    permission_classes = []  # Public endpoint

    @swagger_auto_schema(
        operation_description="List all reviews for a specific villa. Public endpoint.",
        responses={200: VillaReviewSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        villa_id = self.kwargs.get("villa_id")
        return VillaReview.objects.filter(villa_id=villa_id).order_by("-created_at")


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
