from rest_framework import serializers
from .models import *
from hotel.models import *
from masters.serializers import villa_amenity_serializer


from datetime import timedelta


from rest_framework import serializers
from datetime import date as today_date, timedelta
from datetime import date, timedelta


class VillaImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = VillaImage
        fields = ["id", "image"]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else None


class VillaRoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = villa_roomsImage
        fields = ["id", "image"]


class VillaRoomSerializer(serializers.ModelSerializer):
    villa_details = (
        serializers.SerializerMethodField()
    )  # to avoid recursive nesting issues
    room_type_name = serializers.CharField(source="room_type.name", read_only=True)
    images = VillaRoomImageSerializer(many=True, read_only=True)  # room images
    villa_amenity_details = serializers.SerializerMethodField()

    def get_villa_amenity_details(self, obj):
        """Get villa amenities using the serializer"""
        from masters.serializers import villa_amenity_serializer

        amenities = obj.villa_amenities.all()
        return villa_amenity_serializer(amenities, many=True).data

    class Meta:
        model = villa_rooms
        fields = [
            "id",
            "room_type",
            "room_type_name",
            "title",
            "price_per_night",
            "max_guest_count",
            "capacity",
            "view",
            "bed_type",
            "villa_amenity_details",
            "images",
            "villa_details",
        ]
        read_only_fields = ["villa_details", "booking_id", "villa_amenity_details"]

    def get_villa_details(self, obj):
        # avoid full villa -> rooms -> villa recursion
        return {
            "id": obj.villa.id,
            "name": obj.villa.name,
            "villa_id": obj.villa.villa_id,
            "city": obj.villa.city.name if obj.villa.city else None,
            "address": obj.villa.address,
        }


from masters.serializers import *
from users.models import User


class VillaUserSerializer(serializers.ModelSerializer):
    """Simple serializer for user details in villa response"""

    class Meta:
        model = User
        fields = ["id", "mobile", "email", "first_name", "last_name", "profile_photo"]
        read_only_fields = fields


class VillaSerializer(serializers.ModelSerializer):
    rooms = VillaRoomSerializer(many=True, read_only=True)
    images = VillaImageSerializer(many=True, read_only=True)
    city = serializers.StringRelatedField()  # or use CitySerializer if needed
    amenities = amenity_serializer(
        many=True, read_only=True
    )  # or use AmenitySerializer
    property_type = property_type_serializer(
        many=False, read_only=True
    )  # property_type is a ForeignKey, not ManyToMany
    main_image = serializers.SerializerMethodField()
    user = VillaUserSerializer(read_only=True)  # Return user details instead of just ID

    min_price = serializers.SerializerMethodField()
    max_price = serializers.SerializerMethodField()
    price_per_night = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    marked_up_price_per_night = serializers.SerializerMethodField()
    is_best_rated = serializers.SerializerMethodField()
    is_like = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = villa
        fields = [
            "id",
            "name",
            "villa_id",
            "user",
            "category",
            "no_of_rooms",
            "amenities",
            "address",
            "city",
            "landmark",
            "pincode",
            "star_rating",
            "overall_rating",
            "villa_star_facility",
            "mrp",
            "main_image",
            "profit_margin",
            "is_featured",
            "description",
            "is_active",
            "created_at",
            "gst_number",
            "gst_certificate",
            "pan_number",
            "account_holder_name",
            "account_number",
            "ifsc_code",
            "bank_name",
            "bank_document",
            "rooms",
            "images",
            "is_recommended",
            "property_type",
            "price_per_night",
            "marked_up_price_per_night",
            "min_price",
            "max_price",
            "is_best_rated",
            "is_like",
            "average_rating",
            "review_count",
        ]

    def get_min_price(self, obj):
        prices = obj.rooms.values_list("price_per_night", flat=True)
        return min(prices) if prices else None

    def get_max_price(self, obj):
        prices = obj.rooms.values_list("price_per_night", flat=True)
        return max(prices) if prices else None

    def get_marked_up_price_per_night(self, obj):
        """
        Return the price with admin-configured markup percentage.
        This is the price that customers will see.
        """
        return obj.get_marked_up_price()

    def get_main_image(self, obj):
        """
        Return absolute URL for main_image.
        """
        request = self.context.get("request")
        if obj.main_image and request:
            return request.build_absolute_uri(obj.main_image.url)
        return obj.main_image.url if obj.main_image else None

    def get_is_best_rated(self, obj):
        """
        Return True if this villa is in the top 10 best-rated villas.
        Rating is based on overall_rating field.
        """
        # Cache the top 10 villa IDs in the serializer context to avoid repeated queries
        if "top_rated_villa_ids" not in self.context:
            from hotel.models import villa

            top_rated_villas = villa.objects.filter(
                is_active=True, go_live=True, overall_rating__isnull=False
            ).order_by("-overall_rating")[:10]
            self.context["top_rated_villa_ids"] = set(
                top_rated_villas.values_list("id", flat=True)
            )

        return obj.id in self.context.get("top_rated_villa_ids", set())

    def get_is_like(self, obj):
        """
        Return True if the current user has liked/favorited this villa.
        Returns False if user is not authenticated or hasn't favorited the villa.
        """
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            from .models import favouritevilla

            return favouritevilla.objects.filter(user=request.user, villa=obj).exists()
        return False

    def get_average_rating(self, obj):
        """
        Calculate and return average rating from all approved reviews.
        """
        from .models import VillaReview
        from django.db.models import Avg

        avg_rating = VillaReview.objects.filter(villa=obj).aggregate(
            avg_rating=Avg("rating")
        )["avg_rating"]

        if avg_rating:
            # Round to 1 decimal place
            return round(float(avg_rating), 1)
        return None

    def get_review_count(self, obj):
        """
        Return total count of approved reviews for this villa.
        """
        from .models import VillaReview

        return VillaReview.objects.filter(villa=obj).count()


class SupportTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = ["id", "subject", "booking", "is_resolved", "created_at"]
        read_only_fields = ["id", "is_resolved", "created_at"]


class TicketMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.name", read_only=True)
    is_from_user = serializers.SerializerMethodField()

    class Meta:
        model = TicketMessage
        fields = [
            "id",
            "ticket",
            "sender",
            "sender_name",
            "message",
            "created_at",
            "is_from_user",
        ]
        read_only_fields = ["sender", "created_at"]

    def get_is_from_user(self, obj):
        request = self.context.get("request")
        return obj.sender == request.user if request else False


class BookingRoomSerializer(serializers.ModelSerializer):
    """Serializer for booking rooms"""

    room_details = serializers.SerializerMethodField()

    class Meta:
        model = BookingRoom
        fields = [
            "id",
            "room",
            "room_details",
            "quantity",
            "price_per_night",
        ]
        read_only_fields = ["price_per_night"]

    def get_room_details(self, obj):
        # Return room details using VillaRoomSerializer
        return VillaRoomSerializer(obj.room, context=self.context).data


class VillaBookingSerializer(serializers.ModelSerializer):

    villa = serializers.PrimaryKeyRelatedField(
        queryset=villa.objects.all(), write_only=True
    )

    # Read-only nested output
    villa_details = VillaSerializer(source="villa", read_only=True)

    # Room selection for Resort/Couple Stay
    rooms = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        write_only=True,
        help_text="List of rooms to book. Format: [{'room_id': 1, 'quantity': 2}, ...]",
    )

    # Read-only booked rooms
    booked_rooms = BookingRoomSerializer(many=True, read_only=True)

    class Meta:
        model = VillaBooking
        exclude = ["user"]

    def __init__(self, *args, **kwargs):
        user = (
            kwargs["context"]["request"].user
            if "context" in kwargs and "request" in kwargs["context"]
            else None
        )
        super().__init__(*args, **kwargs)

        if user and not user.is_superuser:
            self.fields["status"].choices = [("completed", "Completed")]

    def validate(self, data):
        villa = data.get("villa")
        check_in = data.get("check_in")
        check_out = data.get("check_out")
        rooms = data.get("rooms", [])
        booking_type = data.get("booking_type")

        if not check_in or not check_out:
            raise serializers.ValidationError("Check-in and check-out are required.")

        # Validate dates are not in the past
        today = date.today()
        if check_in < today:
            raise serializers.ValidationError("Check-in date cannot be in the past.")

        if check_out < today:
            raise serializers.ValidationError("Check-out date cannot be in the past.")

        if check_in >= check_out:
            raise serializers.ValidationError("Check-out must be after check-in.")

        if not villa:
            raise serializers.ValidationError("Villa must be provided for booking.")

        # Determine property type
        property_type_name = None
        if villa.property_type:
            property_type_name = villa.property_type.name

        # Auto-set booking type based on property type if not provided
        if not booking_type:
            if property_type_name == "Villa":
                data["booking_type"] = "whole_villa"
            else:
                data["booking_type"] = "selected_rooms"

        # Validate based on booking type
        if data["booking_type"] == "whole_villa":
            # Villa: must have price_per_night
            if not villa.price_per_night:
                raise serializers.ValidationError(
                    "Villa does not have a price set. Please set villa price per night."
                )

            # Check if villa is already booked for these dates
            from .models import VillaBooking as BookingModel
            from hotel.models import VillaAvailability

            # Check for conflicting whole villa bookings
            conflicting_bookings = BookingModel.objects.filter(
                villa=villa,
                booking_type="whole_villa",
                check_in__lt=check_out,
                check_out__gt=check_in,
                status__in=["confirmed", "checked_in"],
            ).exclude(id=self.instance.id if self.instance else None)

            if conflicting_bookings.exists():
                raise serializers.ValidationError(
                    f"This villa is already booked for the selected dates. "
                    f"Please choose different dates."
                )

            # Check if villa is closed for any date in the range
            from datetime import timedelta

            current_date = check_in
            while current_date < check_out:
                villa_availability = VillaAvailability.objects.filter(
                    villa=villa, date=current_date
                ).first()

                if villa_availability and not villa_availability.is_open:
                    raise serializers.ValidationError(
                        f"Villa is closed on {current_date}. Please choose different dates."
                    )

                current_date += timedelta(days=1)
        else:
            # Resort/Couple Stay: must have rooms selected
            if not rooms:
                raise serializers.ValidationError(
                    "Rooms must be selected for Resort/Couple Stay bookings."
                )

            # Validate rooms belong to this villa and are available
            from hotel.models import villa_rooms
            from hotel.models import RoomAvailability
            from .models import VillaBooking as BookingModel

            for room_data in rooms:
                room_id = room_data.get("room_id")
                quantity = room_data.get("quantity", 1)

                if not room_id:
                    raise serializers.ValidationError(
                        "room_id is required for each room."
                    )

                try:
                    room = villa_rooms.objects.get(id=room_id, villa=villa)
                except villa_rooms.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Room {room_id} does not belong to this villa."
                    )

                # Check availability for each date
                from datetime import timedelta

                current_date = check_in
                while current_date < check_out:
                    room_availability = RoomAvailability.objects.filter(
                        room=room, date=current_date
                    ).first()

                    # Check existing bookings (exclude current booking if updating)
                    conflicting_bookings = (
                        BookingModel.objects.filter(
                            villa=villa,
                            check_in__lt=check_out,
                            check_out__gt=check_in,
                            status__in=["confirmed", "checked_in", "pending"],
                            booking_type="selected_rooms",
                        )
                        .exclude(id=self.instance.id if self.instance else None)
                        .prefetch_related("booked_rooms")
                    )

                    booked_quantity = 0
                    for booking in conflicting_bookings:
                        for booked_room in booking.booked_rooms.all():
                            if booked_room.room_id == room_id:
                                booked_quantity += booked_room.quantity

                    # If no RoomAvailability record exists, assume room is available (default: 1)
                    # If record exists but available_count is 0, room is marked as booked (offline)
                    if room_availability:
                        available_count = room_availability.available_count
                        # If available_count is 0, room is marked as booked (offline) - not available
                        if available_count == 0:
                            raise serializers.ValidationError(
                                f"Room {room_id} is not available for the selected dates. "
                                f"Room is marked as booked (offline) on {current_date}."
                            )
                    else:
                        # No availability record means room is available by default
                        available_count = 1  # Default: at least 1 room available

                    available = available_count - booked_quantity

                    if available < quantity:
                        raise serializers.ValidationError(
                            f"Room {room_id} is not available for the selected dates. "
                            f"Only {available} room(s) available on {current_date}."
                        )

                    current_date += timedelta(days=1)

        return data

    def create(self, validated_data):
        rooms_data = validated_data.pop("rooms", [])
        booking = VillaBooking.objects.create(**validated_data)

        # If whole villa booking, automatically book all rooms
        if booking.booking_type == "whole_villa":
            from hotel.models import villa_rooms

            all_rooms = villa_rooms.objects.filter(villa=booking.villa)
            for room in all_rooms:
                BookingRoom.objects.create(
                    booking=booking,
                    room=room,
                    quantity=1,  # Each room booked once
                    price_per_night=room.price_per_night,
                )
        else:
            # Create BookingRoom entries for selected rooms
            for room_data in rooms_data:
                from hotel.models import villa_rooms

                room = villa_rooms.objects.get(id=room_data["room_id"])
                BookingRoom.objects.create(
                    booking=booking,
                    room=room,
                    quantity=room_data.get("quantity", 1),
                    price_per_night=room.price_per_night,
                )

        # Recalculate pricing after rooms are added
        # Save again to recalculate pricing with the booked rooms
        booking.save()

        return booking


class FavouriteVillaSerializer(serializers.ModelSerializer):
    class Meta:
        model = favouritevilla
        fields = ["id", "user", "villa"]  # Include 'user' but make it read-only
        read_only_fields = ["user"]


class VillaReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for villa reviews.
    """

    user = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = VillaReview
        fields = [
            "id",
            "user",
            "user_name",
            "villa",
            "rating",
            "comment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]

    def get_user(self, obj):
        """Return user ID"""
        return obj.user.id if obj.user else None

    def get_user_name(self, obj):
        """Return user's full name or mobile number"""
        if obj.user:
            if obj.user.first_name and obj.user.last_name:
                return f"{obj.user.first_name} {obj.user.last_name}"
            elif obj.user.first_name:
                return obj.user.first_name
            else:
                return obj.user.mobile
        return None

    def validate_rating(self, value):
        """Ensure rating is between 1 and 5"""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate(self, data):
        """Ensure user is a customer and hasn't already reviewed this villa"""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            # Check if user is a customer
            if not request.user.is_customer:
                raise serializers.ValidationError("Only customers can create reviews.")

            # Check if user has already reviewed this villa
            villa = data.get("villa") or (
                self.instance.villa if self.instance else None
            )
            if villa:
                existing_review = VillaReview.objects.filter(
                    user=request.user, villa=villa
                ).exclude(pk=self.instance.pk if self.instance else None)
                if existing_review.exists():
                    raise serializers.ValidationError(
                        "You have already reviewed this villa. You can update your existing review."
                    )
        return data
