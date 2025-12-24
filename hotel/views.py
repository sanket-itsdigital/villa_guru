from django.shortcuts import get_object_or_404, render

from masters.filters import EventFilter

# Create your views here.


from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.urls import reverse
from django.http.response import HttpResponseRedirect

from users.permissions import *

from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required(login_url="login_admin")
def vendor_dashboard(request):

    return render(request, "vendor_dashboard.html")


@login_required(login_url="login_admin")
def register_hotel(request):

    if request.method == "POST":
        form = hotel_Form()
        context = {"form": form}

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if not all([first_name, last_name, email, mobile, password, confirm_password]):
            return render(
                request,
                "hotel_registration.html",
                {"error": "All fields are required."},
                context,
            )

        if password != confirm_password:
            return render(
                request,
                "hotel_registration.html",
                {"error": "Passwords do not match."},
                context,
            )

        if User.objects.filter(email=email).exists():
            return render(
                request,
                "hotel_registration.html",
                {"error": "Email already registered."},
                context,
            )

        if User.objects.filter(mobile=mobile).exists():
            return render(
                request,
                "hotel_registration.html",
                {"error": "Mobile number already registered."},
                context,
            )

        try:
            with transaction.atomic():
                # Create user
                user = User.objects.create_user(
                    email=email,
                    mobile=mobile,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_service_provider=True,
                    is_active=False,
                )

                form = hotel_Form(request.POST, request.FILES, user=request.user)

                if form.is_valid():
                    hotel = form.save(commit=False)
                    if not request.user.is_superuser:
                        hotel.user = user
                    hotel.save()
                    form.save_m2m()

                    for img in request.FILES.getlist("image"):
                        HotelImage.objects.create(hotel=hotel, image=img)

                    return redirect("list_hotel")
                else:
                    # Validation failed — raise exception to rollback user
                    raise Exception(f"Form invalid: {form.errors}")

        except Exception as e:
            print("Error:", e)
            # Optional: show custom error message
            return render(
                request,
                "hotel_registration.html",
                {
                    "form": form,
                    "error": "Something went wrong during registration. Please try again.",
                },
            )

    else:
        form = hotel_Form()
        context = {"form": form}
        return render(request, "hotel_registration.html", context)


@login_required(login_url="login_admin")
def add_hotel(request):

    if request.method == "POST":

        form = hotel_Form(request.POST, request.FILES, user=request.user)

        if form.is_valid():
            hotel = form.save(commit=False)
            if not request.user.is_superuser:
                hotel.user = request.user  # auto-assign vendor user
            hotel.save()
            form.save_m2m()  # Save the many-to-many relationships

            for img in request.FILES.getlist("image"):
                HotelImage.objects.create(hotel=hotel, image=img)

            return redirect("list_hotel")

        else:
            print(form.errors)
            context = {"form": form}
            return render(request, "add_hotel.html", context)

    else:

        print(request.user)

        if request.user.is_superuser:

            print("1111")

        elif request.user.is_service_provider:

            print("----------434-----------")
        form = hotel_Form()

        context = {
            "form": form,
        }

        return render(
            request,
            "add_hotel.html",
        )


@login_required(login_url="login_admin")
def view_hotel(request):

    try:
        user_hotel = hotel.objects.prefetch_related(
            Prefetch(
                "rooms",
                queryset=hotel_rooms.objects.select_related(
                    "room_type"
                ).prefetch_related("room_amenities"),
            )
        ).get(user=request.user)
    except hotel.DoesNotExist:
        user_hotel = None

    context = {"data": user_hotel}  # wrapped in a list if template expects iterable

    return render(request, "view_hotel.html", context)


@login_required(login_url="login_admin")
def update_hotel(request, hotel_id):

    instance = hotel.objects.get(id=hotel_id)

    if request.method == "POST":

        instance = hotel.objects.get(id=hotel_id)
        forms = hotel_Form(
            request.POST, request.FILES, instance=instance, user=request.user
        )

        if forms.is_valid():
            hotels = forms.save(commit=False)
            if not request.user.is_superuser:
                hotels.user = request.user  # auto-assign vendor user
            hotels.save()
            forms.save_m2m()

            for img in request.FILES.getlist("image"):
                HotelImage.objects.create(hotel=instance, image=img)

            if request.user.is_superuser:
                return redirect("list_hotel")

            else:

                return redirect("view_hotel")

        else:
            print(forms.errors)
            context = {
                "form": forms,
                "existing_images": instance.images.all() if instance else None,
            }
            return render(request, "add_hotel.html", context)

    else:

        forms = hotel_Form(instance=instance)

        context = {
            "form": forms,
            "existing_images": instance.images.all() if instance else None,
        }

        return render(request, "add_hotel.html", context)


from django.shortcuts import get_object_or_404
from django.db import transaction


@login_required(login_url="login_admin")
def delete_hotel(request, hotel_id):

    hotel_instance = get_object_or_404(hotel, id=hotel_id)

    try:
        with transaction.atomic():
            hotel_instance.user.delete()  # Delete related user
            hotel_instance.delete()  # Delete hotel
    except Exception as e:
        # Optionally: log or show error
        print("Error deleting hotel:", e)

    return HttpResponseRedirect(reverse("list_hotel"))


from django.db.models import Prefetch


@login_required(login_url="login_admin")
def list_hotel(request):

    data = hotel.objects.prefetch_related(
        Prefetch(
            "rooms",
            queryset=hotel_rooms.objects.select_related("room_type").prefetch_related(
                "room_amenities"
            ),
        )
    ).order_by("-id")

    filterset = HotelFilter(request.GET, queryset=data, request=request)
    filtered_bookings = filterset.qs

    # Paginate
    paginator = Paginator(filtered_bookings, 30)  # Show 10 hotels per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "data": page_obj,  # use paginated data
        "filterset": filterset,
        "page_obj": page_obj,
    }

    return render(request, "list_hotel.html", context)


@login_required(login_url="login_admin")
def delete_hotel_image(request, image_id):
    image = get_object_or_404(HotelImage, id=image_id)

    hotel_id = image.hotel.id  # To redirect back to edit page
    image.delete()

    print("-----------------------------------------")

    print(hotel_id)

    return redirect("update_hotel", hotel_id=hotel_id)


@login_required(login_url="login_admin")
def add_hotel_rooms(request):

    if request.method == "POST":

        form = hotel_rooms_Form(request.POST, request.FILES)

        if form.is_valid():
            instance = form.save(commit=False)

            if request.user.is_superuser:
                # Admin: hotel selected in form by dropdown (already present in form.cleaned_data)
                pass  # already handled by form
            else:
                # Vendor: assign hotel based on the user
                try:
                    user_hotel = hotel.objects.get(user=request.user)
                    instance.hotel = user_hotel
                except hotel.DoesNotExist:
                    return HttpResponse("You are not linked to any hotel.", status=403)

            instance.save()
            form.save_m2m()

            for img in request.FILES.getlist("image"):
                hotel_roomsImage.objects.create(hotel_rooms=instance, image=img)

            return redirect("list_hotel_rooms")

        else:
            print(form.errors)
            context = {"form": form}
            return render(request, "add_hotel_rooms.html", context)

    else:

        form = hotel_rooms_Form()

        return render(request, "add_hotel_rooms.html", {"form": form})


@login_required(login_url="login_admin")
def update_hotel_rooms(request, hotel_rooms_id):
    instance = get_object_or_404(hotel_rooms, id=hotel_rooms_id)

    if request.method == "POST":
        form = hotel_rooms_Form(request.POST, request.FILES, instance=instance)

        if form.is_valid():
            room = form.save(commit=False)

            # Ensure the correct hotel is assigned if user is not a superuser
            if not request.user.is_superuser:
                try:
                    user_hotel = hotel.objects.get(user=request.user)
                    room.hotel = user_hotel
                except hotel.DoesNotExist:
                    return HttpResponse("You are not linked to any hotel.", status=403)

            room.save()
            form.save_m2m()

            for img in request.FILES.getlist("image"):
                hotel_roomsImage.objects.create(hotel_rooms=room, image=img)

            return redirect("list_hotel_rooms")
        else:
            print(form.errors)
    else:
        form = hotel_rooms_Form(instance=instance)

    context = {
        "form": form,
        "existing_images": instance.images.all() if instance else None,
    }
    return render(request, "add_hotel_rooms.html", context)


@login_required(login_url="login_admin")
def delete_hotel_rooms(request, hotel_rooms_id):

    hotel_rooms.objects.get(id=hotel_rooms_id).delete()

    return HttpResponseRedirect(reverse("list_hotel_rooms"))


@login_required(login_url="login_admin")
def view_hotel_rooms(request, hotel_id):

    hotel_instance = hotel.objects.get(id=hotel_id)
    data = hotel_rooms.objects.filter(hotel__id=hotel_id)

    context = {"data": data, "hote_name": hotel_instance.name}

    return render(request, "list_hotel_rooms.html", context)


@login_required(login_url="login_admin")
def delete_hotel_room_image(request, image_id):
    image = get_object_or_404(hotel_roomsImage, id=image_id)

    hotel_rooms_id = image.hotel_rooms.id  # To redirect back to edit page
    image.delete()

    print("-----------------------------------------")

    print(hotel_rooms_id)

    return redirect("update_hotel_rooms", hotel_rooms_id=hotel_rooms_id)


@login_required(login_url="login_admin")
def list_hotel_rooms(request):

    if request.user.is_superuser:
        data = hotel.objects.prefetch_related(
            Prefetch(
                "rooms",
                queryset=hotel_rooms.objects.select_related(
                    "room_type"
                ).prefetch_related("room_amenities"),
            )
        )

        filterset = HotelFilter(request.GET, queryset=data, request=request)
        filtered_bookings = filterset.qs

        context = {"data": filtered_bookings, "filterset": filterset}

        return render(request, "list_hotel.html", context)

    else:

        hotel_instance = hotel.objects.get(user=request.user)
        data = hotel_rooms.objects.filter(hotel=hotel_instance)

        context = {"data": data, "hote_name": hotel_instance.name}

        return render(request, "list_hotel_rooms.html", context)


from customer.models import *

import openpyxl


def export_bookings_to_excel(queryset):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Hotel Bookings"

    # Header row
    headers = [
        "Booking ID",
        "Hotel",
        "Room",
        "Room Count",
        "User",
        "Status",
        "Check-In",
        "Check-Out",
        "Guests",
        "Childs",
        "Name",
        "Phone",
        "Email",
    ]
    sheet.append(headers)

    # Data rows
    for booking in queryset:
        sheet.append(
            [
                booking.booking_id,
                booking.hotel.name if booking.hotel else "",
                str(booking.room.room_type) if booking.room.room_type else "",
                booking.no_of_rooms,
                booking.user.first_name if booking.user else "Guest",
                booking.status,
                booking.check_in.strftime("%Y-%m-%d"),
                booking.check_out.strftime("%Y-%m-%d"),
                booking.guest_count,
                booking.child_count,
                booking.phone_number,
                booking.email,
            ]
        )

    # Response
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="hotel_bookings.xlsx"'
    workbook.save(response)
    return response


@login_required(login_url="login_admin")
def list_hotel_bookings(request):
    # queryset = HotelBooking.objects.filter(payment_status = "paid").order_by('-id') if request.user.is_superuser else HotelBooking.objects.filter(hotel__user=request.user, payment_status = "paid").order_by('-id')
    queryset = queryset = (
        HotelBooking.objects.all().order_by("-id")
        if request.user.is_superuser
        else HotelBooking.objects.filter(hotel__user=request.user).order_by("-id")
    )

    filterset = HotelBookingFilter(request.GET, queryset=queryset, request=request)
    filtered_bookings = filterset.qs

    # ✅ Check if "export" is requested
    if "export" in request.GET:
        return export_bookings_to_excel(filtered_bookings)

    paginator = Paginator(filtered_bookings, 30)  # Show 10 hotels per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    total_earning = (
        filtered_bookings.aggregate(total=Sum("hotel_earning"))["total"] or 0
    )

    context = {
        "data": page_obj,
        "filterset": filterset,
        "total_earning": total_earning,
    }
    return render(request, "list_hotel_bookings.html", context)


from django.utils import timezone
from datetime import date


@login_required(login_url="login_admin")
def list_hotel_future_bookings(request):

    today = date.today()

    base_queryset = HotelBooking.objects.filter(
        check_in__gt=today, payment_status="paid"
    )

    if request.user.is_superuser:
        queryset = base_queryset
    else:
        queryset = base_queryset.filter(hotel__user=request.user)

    filterset = HotelBookingFilter(request.GET, queryset=queryset, request=request)
    filtered_bookings = filterset.qs

    paginator = Paginator(filtered_bookings, 30)  # Show 10 hotels per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    total_earning = (
        filtered_bookings.aggregate(total=Sum("hotel_earning"))["total"] or 0
    )

    context = {
        "data": page_obj,
        "filterset": filterset,
        "total_earning": total_earning,
    }
    return render(request, "list_hotel_bookings.html", context)


from customer.forms import *


# def send_invoice(request, subject, body, booking_id):
#     booking = get_object_or_404(HotelBooking, id=booking_id)

#     # Generate HTML and PDF
#     html_file_path = generate_invoice_html(booking, request)
#     pdf_file_path = os.path.join(tempfile.gettempdir(), f"invoice_{booking.id}.pdf")
#     html_to_pdf_with_chromium(html_file_path, pdf_file_path)

#     # Create email
#     email = EmailMessage(
#         subject=subject,
#         body=body,
#         from_email='rabbitstay1@gmail.com',
#         to=['pratikgosavi654@gmail.com'],
#     )

#     # Attach PDF
#     if os.path.exists(pdf_file_path):
#         with open(pdf_file_path, 'rb') as f:
#             email.attach(f"invoice_{booking.id}.pdf", f.read(), 'application/pdf')

#     email.send()

#     # Optional: Clean up temp files
#     os.remove(html_file_path)
#     os.remove(pdf_file_path)

#     return HttpResponse("Email with PDF sent successfully!")


@login_required(login_url="login_admin")
def update_hotel_bookings(request, booking_id):

    if request.user.is_superuser:

        instance = HotelBooking.objects.get(id=booking_id)

    else:

        instance = HotelBooking.objects.get(hotel__user=request.user, id=booking_id)

    if request.method == "POST":

        print("--------------------")

        form = HotelBookingStatusForm(request.POST, instance=instance)

        print("--------------------")

        if form.is_valid():
            updated_booking = form.save()
            print("--------------------")

            if updated_booking.status == "completed":
                print("Booking has been marked as completed.")

                generate_invoice_pdf(request, updated_booking.id)

            return redirect("list_hotel_bookings")

        else:

            print("------12--------------")

            print(form.errors)
            context = {"form": form}
            return render(request, "update_hotel_bookings.html", context)

    else:

        form = HotelBookingStatusForm(instance=instance, user=request.user)

        context = {"form": form}
        return render(request, "update_hotel_bookings.html", context)


@login_required(login_url="login_admin")
def view_hotel_bookings(request, booking_id):

    instance = HotelBooking.objects.get(id=booking_id)

    form = HotelBookingStatusForm(instance=instance, user=request.user)

    context = {"form": form}
    return render(request, "view_hotel_bookings.html", context)


from django.db.models import Sum

from .filters import *
import openpyxl
from openpyxl.utils import get_column_letter


def export_earning_to_excel(bookings):
    # Create workbook & sheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Hotel Earnings"

    # Header row
    headers = [
        "Booking ID",
        "Hotel",
        "Room",
        "Guest Name",
        "Phone",
        "Email",
        "Check In",
        "Check Out",
        "Nights",
        "No of Rooms",
        "Base Amount",
        "GST",
        "TCS",
        "TDS",
        "Commission",
        "Commission GST",
        "Total Amount",
        "Hotel Earning",
        "Status",
        "Created At",
    ]
    ws.append(headers)

    # Data rows
    for booking in bookings:
        nights = (booking.check_out - booking.check_in).days or 1
        ws.append(
            [
                booking.booking_id,
                booking.hotel.name if booking.hotel else "",
                (
                    booking.room.room_type.name
                    if booking.room and booking.room.room_type
                    else ""
                ),
                f"{booking.first_name} {booking.last_name}",
                booking.phone_number,
                booking.email,
                booking.check_in.strftime("%d-%m-%Y"),
                booking.check_out.strftime("%d-%m-%Y"),
                nights,
                booking.no_of_rooms,
                float(booking.base_amount),
                float(booking.gst_amount),
                float(booking.tcs_amount),
                float(booking.tds_amount),
                float(booking.commission_amount),
                float(booking.commission_gst),
                float(booking.total_amount),
                float(booking.hotel_earning),
                booking.get_status_display(),
                booking.created_at.strftime("%d-%m-%Y %H:%M"),
            ]
        )

    # Adjust column width
    for col in ws.columns:
        max_length = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        ws.column_dimensions[col_letter].width = max_length + 2

    # Prepare response
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="hotel_earnings.xlsx"'
    wb.save(response)
    return response


@login_required(login_url="login_admin")
def list_hotel_earning(request):

    queryset = (
        HotelBooking.objects.filter(payment_status="paid").order_by("-id")
        if request.user.is_superuser
        else HotelBooking.objects.filter(
            hotel__user=request.user, payment_status="paid"
        ).order_by("-id")
    )

    filterset = HotelBookingFilter(request.GET, queryset=queryset, request=request)
    filtered_bookings = filterset.qs
    if "export" in request.GET:
        return export_earning_to_excel(filtered_bookings)
    total_earning = (
        filtered_bookings.aggregate(total=Sum("hotel_earning"))["total"] or 0
    )

    context = {
        "data": filtered_bookings,
        "filterset": filterset,
        "total_earning": total_earning,
    }
    return render(request, "list_hotel_earning.html", context)


# from django.shortcuts import get_object_or_404
# from django.template.loader import render_to_string
# from django.http import HttpResponse
# from xhtml2pdf import pisa
# import io

import io
from django.http import HttpResponse

from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from django.template.loader import render_to_string
import io

import tempfile
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.http import JsonResponse  # optional, if returning a JSON response
from django.conf import settings  #

# from playwright.sync_api import sync_playwright

import os

import base64


# def generate_invoice_html(booking, request):

#     with open(os.path.join(settings.BASE_DIR, 'static/images/Villa_Guru.png'), 'rb') as img_file:
#         logo_base64 = base64.b64encode(img_file.read()).decode('utf-8')

#     html_content = render_to_string('from_owner_to_hotel_invoice.html', {
#         'booking': booking,
#         'request': request,
#         'logo_base64': logo_base64
#     })

#     tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.html', dir=settings.BASE_DIR)
#     tmp.write(html_content.encode('utf-8'))
#     tmp.close()
#     return tmp.name  # return the HTML file path

# from playwright.sync_api import sync_playwright

# def html_to_pdf_with_chromium(html_file_path, output_pdf_path):
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True)
#         page = browser.new_page()
#         page.goto(f'file://{html_file_path}', wait_until='networkidle')
#         page.pdf(path=output_pdf_path, format="A4", print_background=True)
#         browser.close()

# def generate_invoice_pdf(request, booking_id):

#     booking = get_object_or_404(HotelBooking, id=booking_id)

#     html_file_path = generate_invoice_html(booking, request)
#     pdf_file_path = os.path.join(tempfile.gettempdir(), f"invoice_{booking.id}.pdf")

#     html_to_pdf_with_chromium(html_file_path, pdf_file_path)

#     with open(pdf_file_path, 'rb') as f:
#         pdf_data = f.read()

#     # Cleanup
#     os.remove(html_file_path)
#     os.remove(pdf_file_path)

#     return HttpResponse(pdf_data, content_type='application/pdf')


import requests


def generate_invoice_pdf(request, booking_id):
    booking = get_object_or_404(HotelBooking, id=booking_id)
    print("------------------------")
    print(booking.hotel.user.email)
    # Generate base64 logo for the template
    with open(
        os.path.join(settings.BASE_DIR, "static/images/Villa_Guru.png"), "rb"
    ) as img_file:
        logo_base64 = base64.b64encode(img_file.read()).decode("utf-8")

    # Render HTML
    html_content = render_to_string(
        "from_owner_to_hotel_invoice.html",
        {"booking": booking, "request": request, "logo_base64": logo_base64},
    )
    subject = "Invoice against Bookinid " + str(booking_id)

    # Generate PDF using html2pdf.app
    response = requests.post(
        "https://api.html2pdf.app/v1/generate",
        json={
            "html": html_content,
            "apiKey": settings.HTML2PDF_API_KEY,
            "options": {"printBackground": True, "margin": "1cm", "pageSize": "A4"},
        },
    )

    if response.status_code != 200:
        return HttpResponse(f"PDF generation failed: {response.text}", status=400)

    pdf_bytes = response.content
    print("------------------------")
    print(booking.hotel.user.email)
    # Compose email
    email = EmailMessage(
        subject=subject,
        body="Hi, attached pdf for invoice",
        from_email="Rabbitstay221@gmail.com",
        # to=[booking.hotel.user.email],
        to=[booking.hotel.user.email],
    )
    email.attach(f"invoice_{booking.id}.pdf", pdf_bytes, "application/pdf")
    email.send()

    return HttpResponse("Email with PDF sent successfully!")


from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime, timedelta
from django.contrib import messages


from collections import defaultdict
import json
from collections import defaultdict


@login_required
def update_hotel_availability(request):

    hotel_obj = hotel.objects.get(user=request.user)

    if request.method == "POST":
        selected_date = request.POST.get("selected_date")
        selected_date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()

        for room in hotel_rooms.objects.filter(hotel=hotel_obj):
            field_name = f"availability_{room.id}"
            count = request.POST.get(field_name)

            if count is not None and count != "":

                # Save/update room availability
                RoomAvailability.objects.update_or_create(
                    room=room,
                    date=selected_date_obj,
                    defaults={"available_count": count},
                )

        messages.success(request, f"Availability updated for {selected_date}")
        return redirect("update_hotel_availability")

    hotel_obj = hotel.objects.get(user=request.user)

    raw_availability = RoomAvailability.objects.filter(room__hotel=hotel_obj)

    # Build JSON: { "2025-07-05": { "8": 5, "9": 3 } }
    availability_data = defaultdict(dict)
    for entry in raw_availability:
        availability_data[entry.date.isoformat()][
            str(entry.room.id)
        ] = entry.available_count

    # Combine room data by date for single event display
    grouped = defaultdict(list)
    for entry in raw_availability:
        grouped[entry.date.isoformat()].append(
            f"{entry.room.room_type}: {entry.available_count} rooms"
        )

    events = [
        {"title": "<br>".join(labels), "start": date, "color": "#007bff"}
        for date, labels in grouped.items()
    ]

    print(json.dumps(availability_data))

    context = {
        "rooms": hotel_rooms.objects.filter(hotel=hotel_obj),
        "availability_json": json.dumps(availability_data),
        "events": json.dumps(events),
    }

    return render(request, "update_hotel_availability.html", context)


from datetime import datetime, timedelta
from collections import defaultdict
import json


@login_required
def update_from_to_hotel_availability(request):
    hotel_obj = hotel.objects.get(user=request.user)

    if request.method == "POST":
        from_date = request.POST.get("from_date")
        to_date = request.POST.get("to_date")

        try:
            from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date_obj = datetime.strptime(to_date, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            messages.error(request, "Invalid date range")
            return redirect("update_hotel_availability")

        if from_date_obj > to_date_obj:
            messages.error(request, "'From' date must be before 'To' date.")
            return redirect("update_hotel_availability")

        failed_updates = defaultdict(list)

        for room in hotel_rooms.objects.filter(hotel=hotel_obj):
            field_name = f"availability_{room.id}"
            count = request.POST.get(field_name)

            if count is not None and count != "":
                new_count = int(count)

                current_date = from_date_obj
                while current_date <= to_date_obj:
                    # Count confirmed bookings on this date
                    confirmed_count = HotelBooking.objects.filter(
                        hotel=hotel_obj,
                        room=room,
                        status="confirmed",
                        check_in__lte=current_date,
                        check_out__gte=current_date,
                    ).count()

                    if new_count < confirmed_count:
                        failed_updates[room.room_type].append(current_date)
                    else:
                        RoomAvailability.objects.update_or_create(
                            room=room,
                            date=current_date,
                            defaults={"available_count": new_count},
                        )

                    current_date += timedelta(days=1)

        if failed_updates:
            for room_type, dates in failed_updates.items():
                date_strs = ", ".join(d.strftime("%Y-%m-%d") for d in dates)
                messages.warning(
                    request,
                    f"Could not update availability for '{room_type}' on: {date_strs} "
                    f"due to existing confirmed bookings.",
                )
        else:
            messages.success(
                request,
                f"Availability successfully updated from {from_date} to {to_date}.",
            )

        return redirect("update_hotel_availability")

    return redirect("update_hotel_availability")
