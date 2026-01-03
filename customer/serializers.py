from rest_framework import serializers
from .models import *
from hotel.models import *
from masters.serializers import villa_amenity_serializer


from datetime import timedelta


from rest_framework import serializers
from datetime import date as today_date, timedelta
from datetime import date, timedelta


class VillaImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VillaImage
        fields = ["id", "image"]


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
            "refundable",
            "meals_included",
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
        fields = ['id', 'mobile', 'email', 'first_name', 'last_name', 'profile_photo']
        read_only_fields = fields


class VillaSerializer(serializers.ModelSerializer):
    rooms = VillaRoomSerializer(many=True, read_only=True)
    images = VillaImageSerializer(many=True, read_only=True)
    city = serializers.StringRelatedField()  # or use CitySerializer if needed
    amenities = amenity_serializer(
        many=True, read_only=True
    )  # or use AmenitySerializer
    property_type = property_type_serializer(
        many=True, read_only=True
    )  # or use AmenitySerializer
    main_image = serializers.ImageField(required=False)
    user = VillaUserSerializer(read_only=True)  # Return user details instead of just ID

    min_price = serializers.SerializerMethodField()
    max_price = serializers.SerializerMethodField()
    price_per_night = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    marked_up_price_per_night = serializers.SerializerMethodField()

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


class VillaBookingSerializer(serializers.ModelSerializer):

    villa = serializers.PrimaryKeyRelatedField(
        queryset=villa.objects.all(), write_only=True
    )

    # Read-only nested output
    villa_details = VillaSerializer(source="villa", read_only=True)

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

        if not check_in or not check_out:
            raise serializers.ValidationError("Check-in and check-out are required.")

        if check_in < date.today():
            raise serializers.ValidationError("Check-in cannot be in the past.")

        if check_in >= check_out:
            raise serializers.ValidationError("Check-out must be after check-in.")

        # Villa-level booking: validate villa has price
        if villa:
            if not villa.price_per_night:
                raise serializers.ValidationError(
                    "Villa does not have a price set. Please set villa price per night."
                )
        else:
            raise serializers.ValidationError("Villa must be provided for booking.")

        return data


class FavouriteVillaSerializer(serializers.ModelSerializer):
    class Meta:
        model = favouritevilla
        fields = ["id", "user", "villa"]  # Include 'user' but make it read-only
        read_only_fields = ["user"]
