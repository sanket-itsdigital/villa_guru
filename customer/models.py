from django.db import models
from datetime import timedelta

# Create your models here.


from decimal import Decimal


class VillaBooking(models.Model):

    STATUS_CHOICES = [
        ("confirmed", "Confirmed"),
        ("checked_in", "Check In"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    BOOKING_TYPE_CHOICES = [
        ("whole_villa", "Whole Villa"),
        ("selected_rooms", "Selected Rooms"),
    ]

    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="confirmed"
    )
    
    booking_type = models.CharField(
        max_length=20,
        choices=BOOKING_TYPE_CHOICES,
        default="whole_villa",
        help_text="Type of booking: whole villa or selected rooms",
    )

    booking_id = models.CharField(max_length=20, unique=True, blank=True, null=True)

    user = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, blank=True
    )
    villa = models.ForeignKey("hotel.villa", on_delete=models.CASCADE)
    
    villa_price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Villa price per night (for whole villa booking)",
    )

    check_in = models.DateField()
    check_out = models.DateField()
    guest_count = models.PositiveIntegerField()
    child_count = models.PositiveIntegerField()

    is_for_self = models.BooleanField(default=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    special_request = models.TextField(blank=True, null=True)

    # Financial fields
    base_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, help_text="Villa rate * nights"
    )
    tax_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, help_text="Service Tax or Other"
    )
    gst_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, help_text="GST component"
    )
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, help_text="Final price to user"
    )

    commission_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )
    commission_gst = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    tds_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, help_text="1% TDS on subtotal"
    )
    tcs_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, help_text="1% TCS on subtotal"
    )

    hotel_earning = models.DecimalField(max_digits=10, decimal_places=2, default=5.00)

    payment_type = models.CharField(
        max_length=10,
        choices=[("cash", "Cash at Villa"), ("online", "Online (Razorpay)")],
        blank=True,
        null=True,
    )

    payment_status = models.CharField(
        max_length=15,
        choices=[
            ("pending", "Pending"),
            ("paid", "Paid"),
            ("failed", "Failed"),
            ("refunded", "Refunded"),
        ],
        default="pending",
    )

    payment_id = models.CharField(
        max_length=100, blank=True, null=True, help_text="Razorpay Payment ID"
    )
    order_id = models.CharField(
        max_length=100, blank=True, null=True, help_text="Razorpay Order ID"
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Reference ID for reconciliation",
    )

    paid_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        if not self.booking_id:

            print("----------------")

            last = VillaBooking.objects.order_by("-id").first()
            next_id = (last.id + 1) if last else 1
            print(f"RS-BK{next_id:04d}")
            self.booking_id = f"RS-BK{next_id:04d}"  # RS-BK0001, RS-BK0002, etc.
        else:

            print("--------11----------")

            print(self.booking_id)

        if self.check_in and self.check_out:
            nights = (self.check_out - self.check_in).days or 1
            base = Decimal("0.00")
            
            # Determine property type
            property_type_name = None
            if self.villa and self.villa.property_type:
                property_type_name = self.villa.property_type.name
            
            # Determine booking type based on property type if not explicitly set
            if not self.booking_type:
                if property_type_name == "Villa":
                    self.booking_type = "whole_villa"
                else:
                    self.booking_type = "selected_rooms"
            
            if self.booking_type == "whole_villa":
                # Villa-level booking (whole villa only)
                # Calculate total price using date-specific pricing
                current_date = self.check_in
                daily_prices = []
                
                while current_date < self.check_out:
                    # Get marked-up price for this specific date
                    marked_up_price = self.villa.get_marked_up_price(date=current_date)
                    if marked_up_price:
                        daily_prices.append(marked_up_price)
                        base += marked_up_price
                    else:
                        # Fallback to default price if no date-specific pricing
                        default_price = self.villa.get_marked_up_price()
                        if default_price:
                            daily_prices.append(default_price)
                            base += default_price
                    current_date += timedelta(days=1)
                
                # Store average price per night for display purposes
                if daily_prices:
                    avg_price = sum(daily_prices) / len(daily_prices)
                    if not self.villa_price_per_night:
                        self.villa_price_per_night = avg_price
                    price_per_night = avg_price
                else:
                    # Fallback if no pricing available
                    marked_up_price = self.villa.get_marked_up_price()
                    if not self.villa_price_per_night:
                        self.villa_price_per_night = marked_up_price or Decimal("0.00")
                    price_per_night = (
                        self.villa_price_per_night
                        or marked_up_price
                        or self.villa.price_per_night
                        or Decimal("0.00")
                    )
                    base = price_per_night * nights
            else:
                # Room-based booking (Resort/Couple Stay)
                # Calculate from booked rooms
                # Only access booked_rooms if the instance has been saved (has a primary key)
                if self.pk and hasattr(self, 'booked_rooms'):
                    for booking_room in self.booked_rooms.all():
                        room_total = booking_room.price_per_night * nights * booking_room.quantity
                        base += room_total
                
                # If no rooms booked yet (during initial save), we'll recalculate later
                if base == 0:
                    # Use a placeholder - will be recalculated when rooms are added
                    price_per_night = Decimal("0.00")
                else:
                    price_per_night = base / nights if nights > 0 else Decimal("0.00")

            # Determine GST Rate
            gst_percent = Decimal("0.05") if price_per_night < 7500 else Decimal("0.12")
            gst = base * gst_percent
            subtotal = base + gst

            # Commission and its GST
            commission_percent = Decimal("0.10")
            commission = base * commission_percent
            commission_gst_percent = Decimal("0.18")
            commission_gst = commission * commission_gst_percent

            # TCS and TDS
            tcs_percent = Decimal("0.005")
            tds_percent = Decimal("0.001")
            tcs_amount = base * tcs_percent
            tds_amount = base * tds_percent

            # Final Amount to User
            total_amount = subtotal

            # Villa's Earning
            hotel_net = subtotal - commission - commission_gst - tds_amount - tcs_amount

            # Save fields
            self.base_amount = base
            self.gst_amount = gst
            self.total_amount = total_amount
            self.tax_amount = tcs_amount  # optional, or keep tax_amount separate
            self.commission_amount = commission
            self.commission_gst = commission_gst
            self.tds_amount = tds_amount
            self.tcs_amount = tcs_amount
            self.hotel_earning = hotel_net

        super().save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        user = (
            kwargs["context"]["request"].user
            if "context" in kwargs and "request" in kwargs["context"]
            else None
        )
        super().__init__(*args, **kwargs)

        if user and not user.is_superuser:
            self.fields["status"].choices = [("completed", "Completed")]

    def __str__(self):
        return f"Booking for {self.first_name} at {self.villa.name}"


class SupportTicket(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    booking = models.ForeignKey(VillaBooking, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class TicketMessage(models.Model):
    ticket = models.ForeignKey(
        SupportTicket, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey("users.User", on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class favouritevilla(models.Model):
    """
    Model to store user favorites for:
    - Whole villas (villa is set, room is None)
    - Individual rooms from Resort/Couple Stay (villa is set, room is set)
    """
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    villa = models.ForeignKey("hotel.villa", on_delete=models.CASCADE)
    room = models.ForeignKey(
        "hotel.villa_rooms", 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Room ID for Resort/Couple Stay favorites. Leave null for whole villa favorites."
    )

    class Meta:
        unique_together = [("user", "villa", "room")]

    def __str__(self):
        if self.room:
            return f"{self.user} - {self.villa.name} - {self.room.title or self.room}"
        return f"{self.user} - {self.villa.name}"


class PaymentTransaction(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("online", "Online"),
        ("cash", "Cash"),
    ]

    booking = models.ForeignKey(
        "VillaBooking", on_delete=models.CASCADE, related_name="transactions"
    )

    # Razorpay IDs
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.TextField(blank=True, null=True)

    # General payment fields
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="INR")
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES)
    method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)

    # Extra info
    response_payload = models.JSONField(
        blank=True, null=True
    )  # store full webhook/order response
    remarks = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"Txn {self.razorpay_payment_id or self.id} - {self.status} - {self.amount}"
        )


class VillaReview(models.Model):
    """
    Review model for villas.
    Only customers can create reviews.
    """
    RATING_CHOICES = [
        (1, "1 Star"),
        (2, "2 Stars"),
        (3, "3 Stars"),
        (4, "4 Stars"),
        (5, "5 Stars"),
    ]

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="villa_reviews",
        help_text="Customer who wrote the review",
    )
    villa = models.ForeignKey(
        "hotel.villa",
        on_delete=models.CASCADE,
        related_name="reviews",
        help_text="Villa being reviewed",
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        help_text="Rating from 1 to 5 stars",
    )
    comment = models.TextField(
        help_text="Review comment/feedback",
    )
    is_approved = models.BooleanField(
        default=True,
        help_text="Whether the review has been approved by admin",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "villa")
        ordering = ["-created_at"]
        verbose_name = "Villa Review"
        verbose_name_plural = "Villa Reviews"

    def __str__(self):
        return f"Review by {self.user.first_name or self.user.mobile} for {self.villa.name} - {self.rating} stars"


class BookingRoom(models.Model):
    """
    Model to track which specific rooms are booked in a booking.
    Used for Resort and Couple Stay property types where customers can select specific rooms.
    For Villa property type, all rooms are automatically booked.
    """
    booking = models.ForeignKey(
        VillaBooking,
        on_delete=models.CASCADE,
        related_name="booked_rooms"
    )
    room = models.ForeignKey(
        "hotel.villa_rooms",
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        help_text="Number of rooms of this type booked"
    )
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per night for this room at the time of booking"
    )
    
    class Meta:
        unique_together = ("booking", "room")
        verbose_name = "Booking Room"
        verbose_name_plural = "Booking Rooms"
    
    def __str__(self):
        return f"{self.booking.booking_id} - {self.room} (Qty: {self.quantity})"


class EventBooking(models.Model):
    """
    Model to store event booking information from customers.
    Customers fill a form with their basic details to book an event.
    """
    event = models.ForeignKey(
        "masters.event",
        on_delete=models.CASCADE,
        related_name="bookings",
        help_text="The event being booked"
    )
    name = models.CharField(
        max_length=255,
        help_text="Customer's full name"
    )
    phone_number = models.CharField(
        max_length=20,
        help_text="Customer's phone number"
    )
    email = models.EmailField(
        help_text="Customer's email address"
    )
    number_of_people = models.PositiveIntegerField(
        help_text="Number of people attending the event"
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who made the booking (if logged in)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Event Booking"
        verbose_name_plural = "Event Bookings"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.event.name} ({self.number_of_people} people)"


class Enquiry(models.Model):
    """
    Model to store property enquiry information from customers.
    Customers fill a form with their details to enquire about properties.
    """
    MEAL_CHOICES = [
        ("with_meal", "With Meal"),
        ("without_meal", "Without Meal"),
    ]
    
    name = models.CharField(
        max_length=255,
        help_text="Customer's full name"
    )
    location = models.ForeignKey(
        "masters.city",
        on_delete=models.CASCADE,
        help_text="Location/City for the enquiry"
    )
    check_in = models.DateField(
        help_text="Check-in date"
    )
    check_out = models.DateField(
        help_text="Check-out date"
    )
    property_type = models.ForeignKey(
        "masters.property_type",
        on_delete=models.CASCADE,
        help_text="Type of property (Villa, Resort, Couple Stay)"
    )
    number_of_guests = models.PositiveIntegerField(
        help_text="Total number of guests"
    )
    phone_number = models.CharField(
        max_length=20,
        help_text="Customer's phone number"
    )
    email = models.EmailField(
        help_text="Customer's email address"
    )
    meal_option = models.CharField(
        max_length=20,
        choices=MEAL_CHOICES,
        default="without_meal",
        help_text="Meal option: With Meal or Without Meal"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Enquiry"
        verbose_name_plural = "Enquiries"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.property_type.name} ({self.location.name})"


class EventEnquiry(models.Model):
    """
    Model to store event enquiry information from customers.
    Customers fill a form with their details to enquire about events.
    """
    ENQUIRY_TYPE_CHOICES = [
        ("corporate_events", "Corporate Events"),
        ("wedding_ceremony", "Wedding Ceremony"),
        ("birthday_party", "Birthday Party"),
        ("retirement_party", "Retirement Party"),
        ("other", "Other"),
    ]
    
    name = models.CharField(
        max_length=255,
        help_text="Customer's full name"
    )
    enquiry_type = models.CharField(
        max_length=50,
        choices=ENQUIRY_TYPE_CHOICES,
        help_text="Type of event enquiry"
    )
    phone_number = models.CharField(
        max_length=20,
        help_text="Customer's phone number"
    )
    email = models.EmailField(
        help_text="Customer's email address"
    )
    check_in_datetime = models.DateTimeField(
        help_text="Event check-in date and time"
    )
    check_out_datetime = models.DateTimeField(
        help_text="Event check-out date and time"
    )
    number_of_people = models.PositiveIntegerField(
        help_text="Number of people for the event"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Event Enquiry"
        verbose_name_plural = "Event Enquiries"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.get_enquiry_type_display()} ({self.number_of_people} people)"
