# filters.py
import django_filters
from hotel.models import villa, villa_rooms
from masters.models import villa_amenity, amenity


class VillaRoomFilter(django_filters.FilterSet):
    room_type = django_filters.NumberFilter(field_name="room_type__id")
    title = django_filters.CharFilter(lookup_expr="icontains")
    price_min = django_filters.NumberFilter(
        field_name="price_per_night", lookup_expr="gte"
    )
    price_max = django_filters.NumberFilter(
        field_name="price_per_night", lookup_expr="lte"
    )

    # 👇 Optional fields (recommended)
    bed_type = django_filters.CharFilter(lookup_expr="icontains")
    capacity = django_filters.CharFilter(lookup_expr="icontains")
    view = django_filters.CharFilter(lookup_expr="icontains")

    # 👇 Many-to-many: villa amenities by ID
    villa_amenities = django_filters.ModelMultipleChoiceFilter(
        field_name="villa_amenities__id",
        to_field_name="id",
        queryset=villa_amenity.objects.all(),
    )

    class Meta:
        model = villa_rooms
        fields = [
            "room_type",
            "title",
            "price_min",
            "price_max",
            "bed_type",
            "capacity",
            "view",
            "villa_amenities",
        ]


class AvailableVillaFilter(django_filters.FilterSet):
    """
    Filter class for available villas API.
    Supports filtering by price range, villa_star_facility, and amenities.
    """

    # Price range filters
    min_price = django_filters.NumberFilter(
        field_name="price_per_night", lookup_expr="gte", label="Minimum Price"
    )
    max_price = django_filters.NumberFilter(
        field_name="price_per_night", lookup_expr="lte", label="Maximum Price"
    )

    # Villa star facility filter
    villa_star_facility = django_filters.NumberFilter(
        field_name="villa_star_facility", label="Villa Star Facility"
    )

    # Amenities filter (multiple amenities can be selected)
    amenities = django_filters.ModelMultipleChoiceFilter(
        field_name="amenities",
        queryset=amenity.objects.all(),
        conjoined=False,  # OR logic - villa must have at least one of the selected amenities
        label="Amenities",
    )

    class Meta:
        model = villa
        fields = ["min_price", "max_price", "villa_star_facility", "amenities"]
