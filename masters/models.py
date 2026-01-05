from django.db import models


from users.models import User
from django.utils.timezone import now
from datetime import datetime, timezone

import pytz

ist = pytz.timezone("Asia/Kolkata")


from users.models import User


class amenity(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="amenities/", null=True, blank=True)

    def __str__(self):
        return self.name


class property_type(models.Model):
    PROPERTY_TYPE_CHOICES = [
        ("Villa", "Villa"),
        ("Resort", "Resort"),
        ("Couple Stay", "Couple Stay"),
    ]

    name = models.CharField(
        max_length=50,
        choices=PROPERTY_TYPE_CHOICES,
        unique=True,
        help_text="Type of property",
    )

    def __str__(self):
        return self.get_name_display()


class city(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class villa_amenity(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class room_type(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="room_types",
        help_text="Vendor who created this room type. If null, it's a system-wide room type (admin created)."
    )

    class Meta:
        verbose_name = "Room Type"
        verbose_name_plural = "Room Types"
        # Allow same name for different vendors, but unique per vendor
        unique_together = [("name", "user")]

    def __str__(self):
        if self.user:
            return f"{self.name} (by {self.user.first_name or self.user.mobile})"
        return f"{self.name} (System)"


class villa_type(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class coupon(models.Model):

    TYPE_CHOICES = [
        ("percent", "Percentage"),
        ("amount", "Amount"),
    ]
    type = models.CharField(
        max_length=10, choices=TYPE_CHOICES, default="percent"
    )  # 👈 Add this

    code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=500, null=True, blank=True)
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    image = models.ImageField(upload_to="doctor_images/")
    start_date = models.DateTimeField(default=now)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


class customer_address(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    address = models.TextField()
    landmark = models.CharField(max_length=255, null=True, blank=True)
    pin_code = models.CharField(max_length=10)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)

    def __str__(self):
        return (
            f"Name: {self.name}, "
            f"Type: {self.type}, "
            f"Address: {self.address}, "
            f"Landmark: {self.landmark or 'N/A'}, "
            f"Pin Code: {self.pin_code}, "
            f"City: {self.city}, "
            f"State: {self.state}"
        )


class testimonials(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class event(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    feature_image = models.ImageField(
        upload_to="events/",
        null=True,
        blank=True,
        help_text="Main/feature image for the event",
    )
    itinerary = models.TextField(
        blank=True, null=True, help_text="Event itinerary/schedule"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Event price/amount",
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(
        null=True, blank=True, help_text="Event end date and time"
    )
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class EventImage(models.Model):
    """Model to store multiple gallery images for an event"""

    event = models.ForeignKey(
        event, related_name="gallery_images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="events/gallery/")

    def __str__(self):
        return f"{self.event.name} - Image {self.id}"


class home_banner(models.Model):
    title = models.CharField(max_length=225, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="homeBanners/")
    is_for_web = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class SystemSettings(models.Model):
    """
    System-wide settings that can be configured by admin.
    Only one instance should exist (singleton pattern).
    """

    price_markup_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Percentage markup to add to villa prices (e.g., 10 for 10%)",
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "System Settings"
        verbose_name_plural = "System Settings"

    def __str__(self):
        return f"Price Markup: {self.price_markup_percentage}%"

    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
