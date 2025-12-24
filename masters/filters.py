import django_filters
from .models import *

class EventFilter(django_filters.FilterSet):
    class Meta:
        model = event
        exclude = ['image']  # ⛔ Exclude unsupported field

class couponFilter(django_filters.FilterSet):
    class Meta:
        model = coupon
        exclude = ['image']  # ⛔ Exclude unsupported field


class home_bannerFilter(django_filters.FilterSet):
    class Meta:
        model = home_banner
        exclude = ['image']  # ⛔ Exclude unsupported field
