from django.db import models
from django.db.models import Q
from datetime import timedelta


class villa(models.Model):

    VILLA_CATEGORY_CHOICES = [
        ("Budget", "Budget"),
        ("Mid_range", "Mid-range"),
        ("Premium", "Premium"),
        ("Boutique", "Boutique"),
        # Add more as needed
    ]

    villa_id = models.CharField(max_length=20, unique=True, blank=True, null=True)

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="villas",
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

    VILLA_STAR_FACILITY_CHOICES = [
        (1, "1 Star Villa"),
        (2, "2 Star Villa"),
        (3, "3 Star Villa"),
        (4, "4 Star Villa"),
        (5, "5 Star Villa"),
        (6, "6 Star Villa"),
        (7, "7 Star Villa"),
    ]
    villa_star_facility = models.IntegerField(
        choices=VILLA_STAR_FACILITY_CHOICES,
        null=True,
        blank=True,
        help_text="Villa star facility type (1-7 Star Villa). This is a facility classification, not a rating.",
    )
    mrp = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum Retail Price (MRP) for the villa",
    )
    main_image = models.ImageField(upload_to="hotels/", null=True, blank=True)
    profit_margin = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    markup_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Custom markup percentage for this villa (e.g., 10 for 10%). If not set, system-wide markup will be used.",
    )

    is_featured = models.BooleanField(default=False)
    is_recommended = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    about = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed information about the villa/resort/couple stay property"
    )
    specialties = models.TextField(
        blank=True,
        null=True,
        help_text="Special features, unique selling points, or specialties of the property"
    )
    guest_policy = models.TextField(
        blank=True,
        null=True,
        help_text="Guest policy information for the property"
    )
    room_policy = models.TextField(
        blank=True,
        null=True,
        help_text="Room policy information for the property"
    )
    is_active = models.BooleanField(default=True)
    go_live = models.BooleanField(default=False)
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Villa price per night (for whole villa booking)",
    )
    weekend_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        default=0,
        help_text="Percentage increase for weekend prices (e.g., 25 for 25% increase). Applied to base price on weekends (Friday, Saturday, Sunday).",
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
        Applies weekend pricing if date falls on weekend (Friday, Saturday, Sunday).
        Returns the original price if no markup is set.
        """
        from masters.models import SystemSettings
        from decimal import Decimal
        import calendar

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

        # Apply weekend pricing if date is provided and falls on weekend
        if date and self.weekend_percentage:
            weekday = date.weekday()  # Monday=0, Sunday=6
            # Friday=4, Saturday=5, Sunday=6
            if weekday in [4, 5, 6]:
                weekend_multiplier = Decimal(1) + (self.weekend_percentage / 100)
                base_price = base_price * weekend_multiplier

        # Use villa-specific markup if set, otherwise fall back to system-wide markup
        if self.markup_percentage is not None:
            markup_percentage = self.markup_percentage
        else:
            settings = SystemSettings.get_settings()
            markup_percentage = settings.price_markup_percentage or 0

        if markup_percentage == 0:
            return round(base_price, 2)

        # Calculate: original_price * (1 + markup_percentage/100)
        marked_up_price = base_price * (1 + markup_percentage / 100)
        return round(marked_up_price, 2)

    def get_price_for_date(self, date):
        """
        Get the base price for a specific date (without markup, but with weekend pricing if applicable).
        Returns the date-specific price if exists, otherwise returns default price_per_night.
        Applies weekend pricing if date falls on weekend (Friday, Saturday, Sunday).
        """
        from decimal import Decimal

        # Check for date-specific pricing first
        try:
            date_pricing = VillaPricing.objects.get(villa=self, date=date)
            base_price = date_pricing.price_per_night
        except VillaPricing.DoesNotExist:
            base_price = self.price_per_night

        if not base_price:
            return None

        # Apply weekend pricing if date falls on weekend
        if self.weekend_percentage:
            weekday = date.weekday()  # Monday=0, Sunday=6
            # Friday=4, Saturday=5, Sunday=6
            if weekday in [4, 5, 6]:
                weekend_multiplier = Decimal(1) + (self.weekend_percentage / 100)
                base_price = base_price * weekend_multiplier

        return round(base_price, 2)

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
    
    room_count = models.PositiveIntegerField(
        default=1,
        help_text="Number of physical rooms of this type available in the property"
    )

    class Meta:
        unique_together = [("villa", "room_type")]
        verbose_name = "Villa Room"
        verbose_name_plural = "Villa Rooms"

    def __str__(self):
        return f"{self.room_type.name if self.room_type else 'Room'} (x{self.room_count}) - ₹{self.price_per_night}"


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
    """
    Model to track room availability per date.
    - Stores room_id and available_rooms count for each date
    - Automatically calculates availability from total_room_count - active_bookings
    - Can be manually overridden by vendors to close/reduce availability
    """
    room = models.ForeignKey("hotel.villa_rooms", on_delete=models.CASCADE, related_name="availability_records")
    date = models.DateField()
    available_count = models.PositiveIntegerField(
        default=0,
        help_text="Current available rooms for this date. Automatically calculated from bookings, but can be manually overridden."
    )
    is_manually_closed = models.BooleanField(
        default=False,
        help_text="If True, room is manually closed for this date (vendor override)"
    )

    class Meta:
        unique_together = ("room", "date")
        ordering = ["date", "room"]

    def __str__(self):
        return f"{self.room} - {self.date} - {self.available_count} available"

    def calculate_available_count(self):
        """
        Automatically calculate available rooms for this date based on:
        - Total room count (room.room_count)
        - Active bookings for this date
        Returns the calculated available count.
        """
        from customer.models import VillaBooking, BookingRoom
        from datetime import date as date_class
        
        # Get total room count
        total_rooms = self.room.room_count if hasattr(self.room, 'room_count') and self.room.room_count else 1
        
        # If manually closed, return 0
        if self.is_manually_closed:
            return 0
        
        # Get all active bookings for this room on this date
        # Booking overlaps if: booking.check_in < date+1 AND booking.check_out > date
        active_bookings = VillaBooking.objects.filter(
            booked_rooms__room=self.room,
            check_in__lt=self.date + timedelta(days=1),  # Booking starts before or on this date
            check_out__gt=self.date,  # Booking ends after this date
            booking_type="selected_rooms",
        ).exclude(
            status="cancelled"  # Exclude cancelled bookings
        ).filter(
            # Include paid or active bookings
            Q(payment_status="paid") | 
            Q(status__in=["confirmed", "checked_in", "pending"])
        ).distinct()
        
        # Calculate total booked quantity for this date
        total_booked = 0
        for booking in active_bookings:
            booking_room = booking.booked_rooms.filter(room=self.room).first()
            if booking_room:
                total_booked += booking_room.quantity
        
        # Available = total - booked
        available = total_rooms - total_booked
        return max(0, available)  # Ensure non-negative
    
    def update_availability(self):
        """
        Update available_count based on current bookings.
        Call this method to refresh availability when bookings change.
        """
        if not self.is_manually_closed:
            self.available_count = self.calculate_available_count()
            self.save(update_fields=['available_count'])
    
    @classmethod
    def get_or_calculate_availability(cls, room, date):
        """
        Get or create RoomAvailability record and calculate availability automatically.
        If record doesn't exist, creates it with calculated availability.
        If exists and not manually closed, updates it with current calculated availability.
        This method ensures availability is always current based on actual bookings.
        """
        room_avail, created = cls.objects.get_or_create(
            room=room,
            date=date,
            defaults={"available_count": 0, "is_manually_closed": False}  # Will be calculated below
        )
        
        # Calculate and update availability if not manually closed
        if not room_avail.is_manually_closed:
            calculated = room_avail.calculate_available_count()
            # Always update to ensure it's current (bookings may have changed)
            if room_avail.available_count != calculated:
                room_avail.available_count = calculated
                room_avail.save(update_fields=['available_count'])
        
        return room_avail


# Signal to auto-update room availability when bookings change
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from customer.models import VillaBooking, BookingRoom


@receiver(post_save, sender=VillaBooking)
@receiver(post_delete, sender=VillaBooking)
def update_room_availability_on_booking_change(sender, instance, **kwargs):
    """
    Automatically update room availability when bookings are created, updated, or deleted.
    This ensures availability is always current.
    """
    if instance.booking_type == "selected_rooms":
        from datetime import timedelta
        
        # Update availability for all dates in the booking range
        current_date = instance.check_in
        while current_date < instance.check_out:
            # Get all rooms booked in this booking
            booked_rooms = instance.booked_rooms.all()
            for booked_room in booked_rooms:
                # Use the automatic calculation method
                RoomAvailability.get_or_calculate_availability(
                    room=booked_room.room,
                    date=current_date
                )
            current_date += timedelta(days=1)


@receiver(post_save, sender=BookingRoom)
@receiver(post_delete, sender=BookingRoom)
def update_room_availability_on_booking_room_change(sender, instance, **kwargs):
    """
    Automatically update room availability when BookingRoom records change.
    """
    booking = instance.booking
    if booking and booking.booking_type == "selected_rooms":
        from datetime import timedelta
        
        # Update availability for all dates in the booking range
        current_date = booking.check_in
        while current_date < booking.check_out:
            # Use the automatic calculation method
            RoomAvailability.get_or_calculate_availability(
                room=instance.room,
                date=current_date
            )
            current_date += timedelta(days=1)


class VillaPricing(models.Model):
    """
    Model to store date-specific pricing for villas.
    Allows vendors to set different prices for different dates.
    """

    villa = models.ForeignKey(
        "hotel.villa", on_delete=models.CASCADE, related_name="date_pricing"
    )
    date = models.DateField()
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per night for this specific date",
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


class RoomPricing(models.Model):
    """
    Model to store date-specific pricing for individual rooms.
    Used for Resort and Couple Stay properties where rooms have individual pricing.
    """

    room = models.ForeignKey(
        "hotel.villa_rooms", on_delete=models.CASCADE, related_name="date_pricing"
    )
    date = models.DateField()
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per night for this specific room and date",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("room", "date")
        ordering = ["date"]
        verbose_name = "Room Pricing"
        verbose_name_plural = "Room Pricings"

    def __str__(self):
        return f"{self.room.room_type.name if self.room.room_type else 'Room'} - {self.date} - ₹{self.price_per_night}"
