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
from hotel.models import villa, villa_rooms, RoomAvailability

class VillaBookingViewSet(viewsets.ModelViewSet):
    queryset = VillaBooking.objects.filter(payment_status = "paid").order_by("-id")
    serializer_class = VillaBookingSerializer

    def perform_create(self, serializer):
        request_id = uuid.uuid4()
        print(f"🚨 perform_create() called for booking — ID: {request_id}")

        with transaction.atomic():
            booking = serializer.save(user=self.request.user)
            print(f"➡️  Booking saved: {booking.pk}, Rooms: {booking.no_of_rooms}")

            # --- Room availability handling (only for room-based bookings) ---
            if booking.room:
                # Room-based booking: check and update room availability
                room = booking.room
                check_in = booking.check_in
                check_out = booking.check_out
                quantity = booking.no_of_rooms

                total_days = (check_out - check_in).days
                booking_dates = [check_in + timedelta(days=i) for i in range(total_days)]

                availabilities = RoomAvailability.objects.select_for_update().filter(
                    room=room,
                    date__in=booking_dates
                )

                if availabilities.count() != total_days:
                    raise ValidationError("Some dates are missing availability records.")

                insufficient = [a.date for a in availabilities if a.available_count < quantity]
                if insufficient:
                    date_str = ", ".join(str(d) for d in insufficient)
                    raise ValidationError(f"Only limited rooms available on: {date_str}")

                for avail in availabilities:
                    avail.available_count -= quantity
                    avail.save()
            else:
                # Villa-level booking: whole villa is booked, no room availability check needed
                print(f"✅ Villa-level booking: {booking.villa.name} booked as whole villa")

            # --- ✅ Create Razorpay order here ---
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            amount = booking.total_amount  # use your booking amount
            order_data = {
                "amount": int(amount * 100),  # in paise
                "currency": "INR",
                "receipt": f"booking_{booking.id}",
                "payment_capture": 1,  # 👈 auto capture payment
                "notes": {             # 👈 custom metadata
                    "booking_id": str(booking.id),
                    "user_id": str(self.request.user.id),
                }
            }

            order = client.order.create(order_data)

            # Save order_id in booking
            booking.order_id = order["id"]
            booking.save()
            print(f"✅ Razorpay order created: {order['id']} for booking {booking.id}")

    def get_queryset(self):
        return VillaBooking.objects.filter(payment_status__in = ["paid", "pending"], user=self.request.user).order_by('-id')



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
                return Response({"error": "check_in and check_out are required"}, status=400)

            # Determine pricing: room-based or villa-based
            if room_id:
                # Room-based pricing (legacy)
                room = villa_rooms.objects.get(id=room_id)
                price_per_night = room.price_per_night
                nights = (date.fromisoformat(check_out) - date.fromisoformat(check_in)).days or 1
                base = price_per_night * nights * no_of_rooms
            elif hotel_id:
                # Villa-based pricing (whole villa)
                villa_obj = villa.objects.get(id=hotel_id)
                if not villa_obj.price_per_night:
                    return Response({"error": "Villa does not have a price set"}, status=400)
                # Use marked-up price for customer display
                price_per_night = villa_obj.get_marked_up_price() or villa_obj.price_per_night
                nights = (date.fromisoformat(check_out) - date.fromisoformat(check_in)).days or 1
                base = price_per_night * nights  # Whole villa, no_of_rooms not used
            else:
                return Response({"error": "Either room_id or hotel_id is required"}, status=400)

            gst_percent = Decimal('0.05') if price_per_night < 7500 else Decimal('0.12')
            gst = base * gst_percent
            subtotal = base + gst

            tcs = base * Decimal('0.005')
            tds = base * Decimal('0.001')

            return Response({
                "nights": nights,
                "price_per_night": price_per_night,
                "base_amount": base,
                "gst_amount": gst,
                "total_amount": subtotal,
                "tds_amount": tds,
                "tcs_amount": tcs,
            })

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


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def cancelltation_policy(request):

    return render(request, 'cancelltation_policy.html')


@csrf_exempt
def guest_policy(request):

    return render(request, 'guest_policy.html')


@csrf_exempt
def privacy_policy(request):

    return render(request, 'privacy_policy.html')

@csrf_exempt
def terms_condition(request):

    return render(request, 'terms_condition.html')



class VillaListAPIView(generics.ListAPIView):
    serializer_class = VillaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = VillaFilter

    def get_queryset(self):
        return villa.objects.annotate(
            room_count=Count('rooms')
        ).filter(
            go_live=True,
            is_active=True,
            room_count__gt=0
        )
    
    def get_filterset_kwargs(self):
        kwargs = super().get_filterset_kwargs()
        kwargs['request'] = self.request
        return kwargs


class VillaDetailAPIView(generics.RetrieveAPIView):
    queryset = villa.objects.all().order_by('-id')
    serializer_class = VillaSerializer  # this one includes rooms and images
    lookup_url_kwarg = 'hotel_id'



class VillaRoomListAPIView(generics.ListAPIView):
    serializer_class = VillaRoomSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = VillaRoomFilter

    def get_queryset(self):
        hotel_id = self.kwargs.get('hotel_id')
        return villa_rooms.objects.filter(villa_id=hotel_id)



class VillaRoomDetailAPIView(generics.RetrieveAPIView):
    queryset = villa_rooms.objects.all().order_by('-id')
    serializer_class = VillaRoomSerializer
    lookup_url_kwarg = 'room_id'  # matches your URL param





from rest_framework import generics
from rest_framework.exceptions import ValidationError
from django.db.models import Count
from datetime import datetime



class AvailableRoomsAPIView(generics.ListAPIView):
    serializer_class = VillaRoomSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = VillaRoomFilter

    def get_queryset(self):
        from_date_str = self.request.query_params.get('from_date')
        to_date_str = self.request.query_params.get('to_date')
        hotel_id = self.request.query_params.get('hotel_id')

        if not hotel_id:
            raise ValidationError("'hotel_id' is required.")

        if not from_date_str or not to_date_str:
            raise ValidationError("Both 'from_date' and 'to_date' are required.")

        from datetime import datetime
        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
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
            available_count__gt=0
        )

        available_room_ids = (
            availability_qs.values('room')
            .annotate(available_days=Count('date', distinct=True))
            .filter(available_days=total_days)
            .values_list('room', flat=True)
        )

        qs = villa_rooms.objects.filter(id__in=available_room_ids)

        # Apply other filters
        filterset = VillaRoomFilter(self.request.GET, queryset=qs)
        return filterset.qs
    

    

    

class AvailableVillasAPIView(APIView):
    def get(self, request):
        city = request.query_params.get('city')
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')

        if not city or not check_in or not check_out:
            return Response({"error": "city, check_in, and check_out are required."}, status=400)

        try:
            check_in = datetime.strptime(check_in, "%Y-%m-%d").date()
            check_out = datetime.strptime(check_out, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        if check_in >= check_out:
            return Response({"error": "check_out must be after check_in"}, status=400)

        if check_in < date.today():
            return Response({"error": "check_in cannot be in the past."}, status=400)

        # Step 1: Get all rooms from hotels in the given city
        rooms = villa_rooms.objects.select_related('villa').filter(villa__city=city)

        # Step 2: Get all availabilities for the room/date range
        room_ids = rooms.values_list('id', flat=True)
        days = (check_out - check_in).days
        required_dates = {check_in + timedelta(days=i) for i in range(days)}

        availabilities = RoomAvailability.objects.filter(
            room_id__in=room_ids,
            room__hotel__go_live=True,
            date__range=(check_in, check_out - timedelta(days=1)),
            available_count__gte=1
        ).values('room_id', 'date')

        # Step 3: Build room → available_dates mapping
        from collections import defaultdict
        room_to_dates = defaultdict(set)
        for entry in availabilities:
            room_to_dates[entry['room_id']].add(entry['date'])

        # Step 4: Filter rooms that are available for all required dates
        valid_room_ids = [room_id for room_id, dates in room_to_dates.items() if required_dates.issubset(dates)]

        # Step 5: Get unique hotels from those rooms
        available_villas = villa.objects.filter(rooms__id__in=valid_room_ids).distinct()

        return Response(VillaSerializer(available_villas, many=True).data)



from datetime import datetime, time, timedelta

class CancelBookingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        try:
            booking = VillaBooking.objects.get(id=booking_id, user=request.user)
        except VillaBooking.DoesNotExist:
            return Response({'error': 'Booking not found or unauthorized'}, status=404)

        if booking.status == 'cancelled':
            return Response({'message': 'Booking already cancelled'}, status=400)

        checkin_datetime = datetime.combine(booking.check_in, time(hour=9, minute=0))
        now = datetime.now()

        if now > checkin_datetime - timedelta(hours=24):
            return Response({'error': 'Cannot cancel less than 24 hours before check-in (9 AM)'}, status=400)

        # ✅ Restore room availability manually
        current_date = booking.check_in
        while current_date < booking.check_out:
            avail, _ = RoomAvailability.objects.get_or_create(room=booking.room, date=current_date)
            avail.available_count += booking.no_of_rooms
            avail.save()
            current_date += timedelta(days=1)

        booking.status = 'cancelled'
        booking.save()

        return Response({'message': 'Booking cancelled and availability restored successfully'}, status=200)
    
    


from rest_framework import viewsets, permissions

        
class SupportTicketViewSet(viewsets.ModelViewSet):
    serializer_class = SupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SupportTicket.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



from rest_framework import status



class TicketMessageViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        ticket_id = request.query_params.get('ticket_id')
        if not ticket_id:
            return Response({'error': 'ticket_id is required'}, status=400)

        messages = TicketMessage.objects.filter(ticket__id=ticket_id).order_by('created_at')
        serializer = TicketMessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        ticket_id = request.data.get('ticket')
        message = request.data.get('message')

        if not ticket_id or not message:
            return Response({'error': 'ticket and message are required'}, status=400)

        ticket = get_object_or_404(SupportTicket, id=ticket_id)

        new_message = TicketMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            message=message
        )

        serializer = TicketMessageSerializer(new_message, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)





class FavouriteVillaViewSet(viewsets.ModelViewSet):
    queryset = favouritevilla.objects.all().order_by('-id')
    serializer_class = FavouriteVillaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        villa_obj = serializer.validated_data['villa']
        
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
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            client.utility.verify_webhook_signature(
                webhook_body, received_sig, settings.RAZORPAY_WEBHOOK_SECRET
            )
        except razorpay.errors.SignatureVerificationError:
            log("⚠️ Invalid Razorpay webhook signature")
            logger.warning(f"Invalid signature. Headers={dict(request.headers)}, Body={webhook_body}")
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