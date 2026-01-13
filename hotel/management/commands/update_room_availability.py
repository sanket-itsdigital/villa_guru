"""
Management command to automatically update room availability.
This command:
1. Updates availability for all rooms based on current bookings
2. Automatically increases availability when booking dates are past
3. Can be run daily via cron job to keep availability current

Usage:
    python manage.py update_room_availability
    python manage.py update_room_availability --days 30  # Update for next 30 days
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from hotel.models import RoomAvailability, villa_rooms
from customer.models import VillaBooking


class Command(BaseCommand):
    help = 'Automatically update room availability based on current bookings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Number of days from today to update (default: 365)',
        )
        parser.add_argument(
            '--past-days',
            type=int,
            default=0,
            help='Number of past days to also update (default: 0, only future dates)',
        )

    def handle(self, *args, **options):
        days = options['days']
        past_days = options['past_days']
        
        today = date.today()
        start_date = today - timedelta(days=past_days)
        end_date = today + timedelta(days=days)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Updating room availability from {start_date} to {end_date}...'
            )
        )
        
        # Get all rooms from Resort and Couple Stay properties
        rooms = villa_rooms.objects.filter(
            villa__property_type__name__in=["Resort", "Couple Stay"]
        ).select_related('villa', 'room_type')
        
        total_updated = 0
        current_date = start_date
        
        while current_date <= end_date:
            for room in rooms:
                # Use the automatic calculation method
                room_avail = RoomAvailability.get_or_calculate_availability(
                    room=room,
                    date=current_date
                )
                total_updated += 1
            
            current_date += timedelta(days=1)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {total_updated} room availability records.'
            )
        )
        
        # Also clean up old availability records (optional - past 1 year)
        old_date = today - timedelta(days=365)
        deleted_count = RoomAvailability.objects.filter(date__lt=old_date).delete()[0]
        if deleted_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'Cleaned up {deleted_count} old availability records (older than 1 year).'
                )
            )
