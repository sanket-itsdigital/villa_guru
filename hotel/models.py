from django.db import models

# Create your models here.


class villa(models.Model):

    VILLA_CATEGORY_CHOICES = [
        ("Budget", "Budget"),
        ("Mid_range", "Mid-range"),
        ("Premium", "Premium"),
        ("Boutique", "Boutique"),
        # Add more as needed
    ]

    villa_id = models.CharField(max_length=20, unique=True, blank=True, null=True)

    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="villa",
    )
    name = models.CharField(max_length=255)

    category = models.CharField(
        max_length=50, choices=VILLA_CATEGORY_CHOICES, default="Budget"
    )
    property_type = models.ForeignKey(
        "masters.property_type", on_delete=models.CASCADE, null=True, blank=True
    )
    no_of_rooms = models.IntegerField()

    amenities = models.ManyToManyField("masters.amenity", blank=True)
    address = models.TextField()
    city = models.ForeignKey(
        "masters.city", on_delete=models.CASCADE, null=True, blank=True
    )
    landmark = models.TextField(null=True, blank=True)

    pincode = models.IntegerField()
    star_rating = models.IntegerField(null=True, blank=True)
    overall_rating = models.DecimalField(
        max_digits=2, decimal_places=1, null=True, blank=True
    )
    main_image = models.ImageField(upload_to="hotels/", null=True, blank=True)
    profit_margin = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )

    is_featured = models.BooleanField(default=False)
    is_recommended = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    go_live = models.BooleanField(default=False)
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Villa price per night (for whole villa booking)",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ Legal & Tax Info
    gst_number = models.CharField(
        max_length=15,
        help_text="GST Number (15 characters, e.g., 29ABCDE1234F2Z5)",
        null=True,
        blank=True,
    )
    gst_certificate = models.FileField(
        upload_to="hotel_docs/gst_certificates/",
        null=True,
        blank=True,
        help_text="Upload GST Certificate (PDF/Image)",
    )
    pan_number = models.CharField(
        max_length=10, null=True, blank=True, help_text="PAN Card Number (optional)"
    )

    # ✅ Bank Details
    account_holder_name = models.CharField(max_length=255, null=True, blank=True)
    account_number = models.CharField(max_length=30, null=True, blank=True)
    ifsc_code = models.CharField(max_length=15, null=True, blank=True)
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    bank_document = models.FileField(
        upload_to="hotel_docs/bank_docs/",
        null=True,
        blank=True,
        help_text="Upload Cancelled Cheque or Bank Passbook (Image/PDF)",
    )

    def save(self, *args, **kwargs):
        # First save to get ID
        if not self.villa_id:
            super().save(*args, **kwargs)  # Save once to get ID
            self.villa_id = f"RS-{self.id:03d}"
            super().save(update_fields=["villa_id"])  # Save only villa_id
        else:
            super().save(*args, **kwargs)

    def get_marked_up_price(self, date=None):
        """
        Calculate the price with admin-configured markup percentage.
        If date is provided, check for date-specific pricing first.
        Returns the original price if no markup is set.
        """
        from masters.models import SystemSettings
        from decimal import Decimal

        # Check for date-specific pricing first
        if date:
            try:
                date_pricing = VillaPricing.objects.get(villa=self, date=date)
                base_price = date_pricing.price_per_night
            except VillaPricing.DoesNotExist:
                base_price = self.price_per_night
        else:
            base_price = self.price_per_night

        if not base_price:
            return None

        settings = SystemSettings.get_settings()
        markup_percentage = settings.price_markup_percentage or 0

        if markup_percentage == 0:
            return base_price

        # Calculate: original_price * (1 + markup_percentage/100)
        marked_up_price = base_price * (1 + markup_percentage / 100)
        return round(marked_up_price, 2)
    
    def get_price_for_date(self, date):
        """
        Get the base price for a specific date (without markup).
        Returns the date-specific price if exists, otherwise returns default price_per_night.
        """
        try:
            date_pricing = VillaPricing.objects.get(villa=self, date=date)
            return date_pricing.price_per_night
        except VillaPricing.DoesNotExist:
            return self.price_per_night

    def __str__(self):
        return self.name


from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=villa)
def sync_user_status_with_villa(sender, instance, **kwargs):
    if instance.user:
        if instance.user.is_active != instance.is_active:
            instance.user.is_active = instance.is_active
            instance.user.save(update_fields=["is_active"])


class VillaImage(models.Model):
    villa = models.ForeignKey(villa, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="villa_gallery/")


class villa_rooms(models.Model):

    ROOM_TYPE_CHOICES = [
        ("standard", "Standard Room"),
        ("deluxe", "Deluxe Room"),
        ("suite", "Suite"),
        # Add more as needed
    ]

    ROOM_PACKAGE_CHOICES = [
        ("room_only", "Room Only"),
        ("breakfast", "Breakfast Included"),
        ("breakfast_lunch", "Breakfast + Lunch"),
        ("breakfast_dinner", "Breakfast + Dinner"),
        ("all_meals", "Breakfast + Lunch + Dinner"),
    ]

    villa = models.ForeignKey(
        "hotel.villa",
        on_delete=models.CASCADE,
        related_name="rooms",
        null=True,
        blank=True,
    )
    room_type = models.ForeignKey(
        "masters.room_type", on_delete=models.CASCADE, related_name="rooms"
    )
    main_image = models.ImageField(upload_to="hotels/", null=True, blank=True)

    max_guest_count = models.IntegerField()

    title = models.CharField(
        max_length=50, choices=ROOM_PACKAGE_CHOICES, default="room_only"
    )

    description = models.TextField(blank=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    refundable = models.BooleanField(default=True)
    meals_included = models.BooleanField(default=False)
    bed_type = models.CharField(
        max_length=100, blank=True
    )  # e.g., "1 Queen Bed + 1 Double Bed"
    capacity = models.CharField(max_length=100, blank=True)  # e.g., "2 Adults, 1 Child"
    view = models.CharField(max_length=100, blank=True)  # e.g., "Beach View"
    villa_amenities = models.ManyToManyField(
        "masters.villa_amenity", blank=True
    )  # Optional: for extra features

    def __str__(self):
        return f" {self.room_type} - ₹{self.price_per_night}"


class villa_roomsImage(models.Model):
    villa_rooms = models.ForeignKey(
        villa_rooms, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="villa_rooms_gallery/")


class VillaAvailability(models.Model):
    villa = models.ForeignKey("hotel.villa", on_delete=models.CASCADE)
    date = models.DateField()
    is_open = models.BooleanField(default=True)

    class Meta:
        unique_together = ("villa", "date")

    def __str__(self):
        return (
            f"{self.villa.name} - {self.date} - {'Open' if self.is_open else 'Closed'}"
        )


class RoomAvailability(models.Model):
    room = models.ForeignKey("hotel.villa_rooms", on_delete=models.CASCADE)
    date = models.DateField()
    available_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("room", "date")

    def __str__(self):
        return f"{self.room} - {self.date} - {self.available_count} available"


class VillaPricing(models.Model):
    """
    Model to store date-specific pricing for villas.
    Allows vendors to set different prices for different dates.
    """
    villa = models.ForeignKey("hotel.villa", on_delete=models.CASCADE, related_name="date_pricing")
    date = models.DateField()
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per night for this specific date"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("villa", "date")
        ordering = ["date"]
        verbose_name = "Villa Pricing"
        verbose_name_plural = "Villa Pricings"

    def __str__(self):
        return f"{self.villa.name} - {self.date} - ₹{self.price_per_night}"
