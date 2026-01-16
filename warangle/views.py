
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


@login_required(login_url='login_admin')
def list_enquiries(request):
    """
    View to list all property enquiries in admin dashboard.
    Only accessible to superusers.
    Also handles POST requests to create new enquiries.
    """
    from customer.models import Enquiry
    from django.core.paginator import Paginator
    from django.contrib import messages
    from datetime import datetime
    
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to view enquiries.")
        return redirect('dashboard')
    
    # Handle POST request to create new enquiry
    if request.method == 'POST':
        from masters.models import property_type, city
        
        try:
            name = request.POST.get('name')
            location_id = request.POST.get('location')
            check_in_str = request.POST.get('check_in')
            check_out_str = request.POST.get('check_out')
            property_type_id = request.POST.get('property_type')
            number_of_guests = request.POST.get('number_of_guests')
            phone_number = request.POST.get('phone_number')
            email = request.POST.get('email')
            
            # Validate required fields
            if not all([name, location_id, check_in_str, check_out_str, property_type_id, number_of_guests, phone_number, email]):
                messages.error(request, "All fields are required.")
            else:
                # Parse dates
                check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
                check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()
                
                if check_in >= check_out:
                    messages.error(request, "Check-out date must be after check-in date.")
                elif check_in < datetime.now().date():
                    messages.error(request, "Check-in date cannot be in the past.")
                else:
                    # Create enquiry
                    enquiry = Enquiry.objects.create(
                        name=name,
                        location_id=int(location_id),
                        check_in=check_in,
                        check_out=check_out,
                        property_type_id=int(property_type_id),
                        number_of_guests=int(number_of_guests),
                        phone_number=phone_number,
                        email=email
                    )
                    messages.success(request, f"Enquiry created successfully for {enquiry.name}!")
                    return redirect('list_enquiries')
        except Exception as e:
            messages.error(request, f"Error creating enquiry: {str(e)}")
    
    # Get all enquiries
    queryset = Enquiry.objects.all().order_by("-created_at")
    
    # Filter by property type if provided
    property_type_id = request.GET.get("property_type")
    selected_property_type_id = None
    if property_type_id:
        try:
            selected_property_type_id = int(property_type_id)
            queryset = queryset.filter(property_type_id=selected_property_type_id)
        except (ValueError, TypeError):
            pass  # Invalid property_type_id, ignore filter
    
    # Filter by location if provided
    location_id = request.GET.get("location")
    selected_location_id = None
    if location_id:
        try:
            selected_location_id = int(location_id)
            queryset = queryset.filter(location_id=selected_location_id)
        except (ValueError, TypeError):
            pass  # Invalid location_id, ignore filter
    
    # Get all property types and locations for filter dropdowns
    from masters.models import property_type, city
    all_property_types = property_type.objects.all().order_by("name")
    all_locations = city.objects.all().order_by("name")
    
    # Pagination
    paginator = Paginator(queryset, 30)  # Show 30 enquiries per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    # Statistics (based on filtered queryset)
    total_enquiries = queryset.count()
    
    context = {
        "enquiries": page_obj,
        "total_enquiries": total_enquiries,
        "property_types": all_property_types,
        "locations": all_locations,
        "selected_property_type": selected_property_type_id,
        "selected_location": selected_location_id,
    }
    
    return render(request, 'list_enquiries.html', context)






