# filters.py
import django_filters
from customer.models import VillaBooking
from .models import *
from masters.models import *
from users.models import *
from django import forms


class VillaFilter(django_filters.FilterSet):

    name = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains", label="Villa Name"
    )

    villa_id = django_filters.CharFilter(lookup_expr="icontains", label="Villa ID")

    user = django_filters.ModelChoiceFilter(queryset=User.objects.all(), label="User")

    category = django_filters.ChoiceFilter(
        choices=villa.VILLA_CATEGORY_CHOICES, label="Category"
    )

    property_type = django_filters.ModelChoiceFilter(
        queryset=property_type.objects.all(),
        label="Property Type",
        empty_label="All Property Types",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    city = django_filters.ModelChoiceFilter(queryset=city.objects.all(), label="City")

    amenities = django_filters.ModelMultipleChoiceFilter(
        field_name="amenities",
        queryset=amenity.objects.all(),
        conjoined=True,
        label="Amenities",
    )

    pincode = django_filters.NumberFilter(field_name="pincode", label="Pincode")

    star_rating = django_filters.NumberFilter(
        field_name="star_rating", label="Star Rating"
    )

    overall_rating = django_filters.NumberFilter(
        field_name="overall_rating", label="Overall Rating"
    )

    is_featured = django_filters.BooleanFilter(
        field_name="is_featured", label="Is Featured"
    )

    is_recommended = django_filters.BooleanFilter(
        field_name="is_recommended", label="Is Recommended"
    )

    is_active = django_filters.BooleanFilter(field_name="is_active", label="Is Active")

    go_live = django_filters.BooleanFilter(field_name="go_live", label="Go Live")

    class Meta:
        model = villa
        fields = [
            "name",
            "villa_id",
            "user",
            "category",
            "property_type",
            "city",
            "amenities",
            "pincode",
            "star_rating",
            "overall_rating",
            "is_featured",
            "is_recommended",
            "is_active",
            "go_live",
        ]

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        # Hide user filter for non-admins
        if request and not request.user.is_superuser:
            self.filters.pop("user", None)

        # Add Bootstrap class to fields
        for field in self.form.fields.values():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                field.widget.attrs.update({"class": "form-control"})


class VillaRoomFilter(django_filters.FilterSet):

    villa_id = django_filters.CharFilter(
        label="Villa ID",
        method="filter_villa_id",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    villa = django_filters.ModelChoiceFilter(
        queryset=villa.objects.all(),
        empty_label="All Villas",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = villa_rooms
        fields = ["villa", "villa_id"]  # ✅ include villa_id here!

    def filter_villa_id(self, queryset, name, value):
        return queryset.filter(villa__villa_id__icontains=value)

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)


class VillaBookingFilter(django_filters.FilterSet):

    villa = django_filters.ModelChoiceFilter(
        queryset=villa.objects.all(),
        empty_label="All Villas",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    user = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        empty_label="All users",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    booking_id = django_filters.CharFilter(
        field_name="booking_id",
        lookup_expr="icontains",
        label="Booking ID",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    check_in = django_filters.DateFilter(
        field_name="check_in",
        lookup_expr="gte",
        label="Check-in Date ",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    check_out = django_filters.DateFilter(
        field_name="check_out",
        lookup_expr="lte",
        label="Check-out Date ",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    class Meta:
        model = VillaBooking
        fields = ["user", "villa", "check_in", "check_out"]

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        # Hide villa filter for non-admins
        if request and not request.user.is_superuser:
            self.filters.pop("villa", None)
            self.filters.pop("user", None)
