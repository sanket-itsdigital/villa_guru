
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.db.models import Sum
from django.db.models import Count
from django.shortcuts import redirect
# from petprofile.models import *


from customer.models import VillaBooking
from hotel.models import villa
from masters.models import *
from django.db.models import Sum


from django.shortcuts import render
from django.db.models import Sum
import json



def get_booking_percent_by_city():
    total_bookings = VillaBooking.objects.count()

    if total_bookings == 0:
        return {}

    # Assuming villa model has a `city` field
    city_data = (
        VillaBooking.objects
        .values('villa__city__name')
        .annotate(city_count=Count('id'))
    )

    # Format output with percentage
    result = {
        entry['villa__city__name']: round((entry['city_count'] / total_bookings) * 100, 2)
        for entry in city_data
    }

    return result


from django.db.models import Sum
from django.utils.timezone import now
from calendar import month_name
from collections import defaultdict
from datetime import timedelta


def get_monthly_booking_data():
    today = now().date()
    data = defaultdict(int)

    for i in range(12):
        month_date = today.replace(day=1) - timedelta(days=30 * i)
        month = month_date.month
        year = month_date.year

        count = VillaBooking.objects.filter(created_at__year=year, created_at__month=month).count()
        data[month_name[month]] = count

    # Reverse to make chronological (oldest to newest)
    return dict(reversed(data.items()))


@login_required(login_url='login_admin')
def dashboard(request):

    if request.user.is_superuser:
       
       
        bookings_count = VillaBooking.objects.count()
        hotels_count = villa.objects.count()
        city_count = city.objects.count()
        total_collection = VillaBooking.objects.filter(status="completed").aggregate(total=Sum('total_amount'))['total'] or 0

        result = get_booking_percent_by_city()

        monthly_data = get_monthly_booking_data()
        months = list(monthly_data.keys())
        bookings = list(monthly_data.values())


    else:

        hotels_count = None
        city_count = None
        result = None

        bookings_count = VillaBooking.objects.filter(villa__user = request.user).count()
        total_collection = VillaBooking.objects.filter(villa__user = request.user, status="completed").aggregate(total=Sum('total_amount'))['total'] or 0

        monthly_data = get_monthly_booking_data()
        months = list(monthly_data.keys())
        bookings = list(monthly_data.values())


    print(months)
    print(bookings)

  

    context = {
        'bookings_count': bookings_count,
        'hotels_count': hotels_count,
        'city_count': city_count,
        'total_collection': round(total_collection),
        'result': result,

        "months": months,
        "bookings": bookings,
    }

    return render(request, 'adminDashboard.html', context)


@login_required(login_url='login_admin')
def list_event_bookings(request):
    """
    View to list all event bookings in admin dashboard.
    Only accessible to superusers.
    """
    from customer.models import EventBooking
    from masters.models import event
    from django.core.paginator import Paginator
    
    if not request.user.is_superuser:
        from django.contrib import messages
        messages.error(request, "You do not have permission to view event bookings.")
        return redirect('dashboard')
    
    # Get all event bookings
    queryset = EventBooking.objects.all().order_by("-created_at")
    
    # Filter by event if provided
    event_id = request.GET.get("event")
    selected_event_id = None
    if event_id:
        try:
            selected_event_id = int(event_id)
            queryset = queryset.filter(event_id=selected_event_id)
        except (ValueError, TypeError):
            pass  # Invalid event_id, ignore filter
    
    # Get only current and future events for filter dropdown
    from django.utils import timezone
    from django.db.models import Q
    current_time = timezone.now()
    today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Include events that:
    # 1. Start today or in the future (start_date >= today at 00:00:00)
    # 2. OR are currently ongoing (started but not ended yet)
    all_events = event.objects.filter(
        Q(start_date__gte=today_start)  # Events starting today or future
        | (
            Q(start_date__lt=current_time)
            & (Q(end_date__isnull=True) | Q(end_date__gte=current_time))
        )  # Events that have started but haven't ended
    ).order_by("start_date")
    
    # Pagination
    paginator = Paginator(queryset, 30)  # Show 30 bookings per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    # Statistics (based on filtered queryset)
    total_bookings = queryset.count()
    total_people = queryset.aggregate(total=Sum('number_of_people'))['total'] or 0
    
    context = {
        "bookings": page_obj,
        "total_bookings": total_bookings,
        "total_people": total_people,
        "events": all_events,
        "selected_event": selected_event_id,
    }
    
    return render(request, 'list_event_bookings.html', context)






