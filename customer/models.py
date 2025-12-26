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

    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="confirmed"
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
            # Villa-level booking (whole villa only)
            # Calculate total price using date-specific pricing
            nights = (self.check_out - self.check_in).days or 1
            
            # Calculate base amount by summing prices for each day
            base = Decimal("0.00")
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
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    villa = models.ForeignKey("hotel.villa", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "villa")


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
