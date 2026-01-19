import django_filters
from django.db.models import ImageField
from .models import *

# Base FilterSet that excludes ImageFields by default
class BaseFilterSet(django_filters.FilterSet):
    """Base FilterSet that automatically excludes ImageField fields"""
    class Meta:
        filter_overrides = {
            ImageField: {
                'filter_class': django_filters.CharFilter,
            }
        }

class EventFilter(django_filters.FilterSet):
    class Meta:
        model = event
        exclude = ['feature_image']  # ⛔ Exclude unsupported field

class couponFilter(django_filters.FilterSet):
    class Meta:
        model = coupon
        exclude = ['image']  # ⛔ Exclude unsupported field


class home_bannerFilter(django_filters.FilterSet):
    class Meta:
        model = home_banner
        exclude = ['image']  # ⛔ Exclude unsupported field


class AmenityFilter(django_filters.FilterSet):
    class Meta:
        model = amenity
        exclude = ['image']  # ⛔ Exclude unsupported field


class CityFilter(django_filters.FilterSet):
    class Meta:
        model = city
        exclude = ['logo']  # Exclude ImageField


class TestimonialsFilter(django_filters.FilterSet):
    class Meta:
        model = testimonials
        fields = '__all__'  # testimonials has no ImageField


class PropertyTypeFilter(django_filters.FilterSet):
    class Meta:
        model = property_type
        fields = '__all__'  # property_type has no ImageField


class VillaAmenityFilter(django_filters.FilterSet):
    class Meta:
        model = villa_amenity
        fields = '__all__'  # villa_amenity has no ImageField

class VillaTypeFilter(django_filters.FilterSet):
    class Meta:
        model = villa_type
        fields = '__all__'  # villa_type has no ImageField

class CustomerAddressFilter(django_filters.FilterSet):
    class Meta:
        model = customer_address
        fields = '__all__'  # customer_address has no ImageField