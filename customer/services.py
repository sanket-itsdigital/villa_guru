"""
Booking-related service functions (e.g. confirm availability after payment).
"""

from datetime import timedelta


def confirm_booking_availability(booking):
    """
    Update villa/room availability after payment success.
    Call this only when payment_status becomes 'paid' for online bookings,
    or when creating a cash booking.
    """
    from hotel.models import VillaAvailability, RoomAvailability

    if booking.booking_type == "whole_villa":
        current_date = booking.check_in
        while current_date < booking.check_out:
            VillaAvailability.objects.update_or_create(
                villa=booking.villa,
                date=current_date,
                defaults={"is_open": False},
            )
            current_date += timedelta(days=1)
    else:
        booked_rooms = booking.booked_rooms.all()
        current_date = booking.check_in
        while current_date < booking.check_out:
            for booked_room in booked_rooms:
                RoomAvailability.get_or_calculate_availability(
                    room=booked_room.room, date=current_date
                )
            current_date += timedelta(days=1)
