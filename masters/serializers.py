from rest_framework import serializers
from .models import *


class amenity_serializer(serializers.ModelSerializer):
    class Meta:
        model = amenity
        fields = "__all__"


class property_type_serializer(serializers.ModelSerializer):
    class Meta:
        model = property_type
        fields = "__all__"


class city_serializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    
    class Meta:
        model = city
        fields = "__all__"
    
    def get_logo(self, obj):
        """
        Return absolute URL for city logo.
        """
        request = self.context.get("request")
        if obj.logo and request:
            return request.build_absolute_uri(obj.logo.url)
        return obj.logo.url if obj.logo else None


class villa_amenity_serializer(serializers.ModelSerializer):
    class Meta:
        model = villa_amenity
        fields = "__all__"


class villa_type_serializer(serializers.ModelSerializer):
    class Meta:
        model = villa_type
        fields = "__all__"


class coupon_serializer(serializers.ModelSerializer):
    class Meta:
        model = coupon
        fields = "__all__"


class customer_address_serializer(serializers.ModelSerializer):

    class Meta:
        model = customer_address
        fields = "__all__"
        read_only_fields = ["user"]

    def create(self, validated_data):
        # Inject authenticated user manually
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class testimonials_serializer(serializers.ModelSerializer):
    class Meta:
        model = testimonials
        fields = "__all__"


class event_serializer(serializers.ModelSerializer):
    class Meta:
        model = event
        fields = "__all__"


# Step 1: Create a serializer
class HomeBannerSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = home_banner
        fields = [
            "id",
            "title",
            "description",
            "image",
            "category",
            "is_for_web",
            "is_active",
            "created_at",
        ]

    def get_image(self, obj):
        """
        Return absolute URL for banner image.
        """
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else None


class room_type_serializer(serializers.ModelSerializer):
    """Serializer for room types with amenities and images"""

    amenities = villa_amenity_serializer(many=True, read_only=True)
    amenities_list = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    price_per_night = serializers.SerializerMethodField()

    class Meta:
        model = room_type
        fields = [
            "id",
            "name",
            "user",
            "created_by",
            "amenities",
            "amenities_list",
            "images",
            "price_per_night",
        ]
        read_only_fields = ["user"]

    def get_amenities_list(self, obj):
        """Return list of amenity names"""
        return [amenity.name for amenity in obj.amenities.all()]

    def get_created_by(self, obj):
        """Return user details if room type was created by a vendor"""
        if obj.user:
            return {
                "id": obj.user.id,
                "name": f"{obj.user.first_name} {obj.user.last_name}".strip()
                or obj.user.mobile,
                "email": obj.user.email,
            }
        return None

    def get_images(self, obj):
        """Get images from all rooms that use this room type"""
        from hotel.models import villa_roomsImage
        from customer.serializers import VillaRoomImageSerializer

        request = self.context.get("request")

        # Get all rooms that use this room type
        rooms = obj.rooms.all()

        # Collect all images from these rooms
        all_images = []
        seen_image_urls = set()  # To avoid duplicates

        for room in rooms:
            # Get images for this room
            room_images = villa_roomsImage.objects.filter(villa_rooms=room)

            for room_image in room_images:
                # Build absolute URL if request is available
                if room_image.image:
                    if request:
                        image_url = request.build_absolute_uri(room_image.image.url)
                    else:
                        image_url = room_image.image.url

                    # Avoid duplicate images (same URL)
                    if image_url not in seen_image_urls:
                        seen_image_urls.add(image_url)
                        all_images.append({"id": room_image.id, "image": image_url})

        return all_images

    def get_price_per_night(self, obj):
        """
        Get price per night for this room type.
        If context has 'villa', get price from rooms of this room_type in that villa.
        Otherwise, get the first available price from any room using this room_type.
        """
        from hotel.models import villa_rooms
        
        # Check if villa is provided in context (from VillaDetailAPIView)
        villa = self.context.get('villa')
        
        if villa:
            # Get price from rooms of this room_type in the specific villa
            rooms = villa_rooms.objects.filter(
                room_type=obj,
                villa=villa
            ).order_by('price_per_night')
            
            if rooms.exists():
                # Return the price from the first room (or could return min/max)
                return float(rooms.first().price_per_night)
        
        # Fallback: get price from any room using this room_type
        rooms = obj.rooms.all().order_by('price_per_night')
        if rooms.exists():
            return float(rooms.first().price_per_night)
        
        return None
