from django.shortcuts import get_object_or_404, render

from masters.filters import EventFilter

# Create your views here.


from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from django.shortcuts import render, redirect
from django.urls import reverse
from django.http.response import HttpResponseRedirect
from .serializers import *

from users.permissions import *

from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger





# @login_required(login_url='login_admin')
# def add_doctor(request):

#     if request.method == 'POST':

#         forms = doctor_Form(request.POST, request.FILES)

#         if forms.is_valid():
#             forms.save()
#             return redirect('list_doctor')
#         else:
#             print(forms.errors)
#             context = {
#                 'form': forms
#             }
#             return render(request, 'add_doctor.html', context)

#     else:

#         forms = doctor_Form()

#         context = {
#             'form': forms
#         }
#         return render(request, 'add_doctor.html', context)


# from django.views.decorators.csrf import csrf_exempt

# @login_required(login_url='login_admin')
# @csrf_exempt
# def add_doctor_json(request):

#     if request.method == 'POST':
#         form = doctor_Form(request.POST, request.FILES)

#         if form.is_valid():
#             form.save()
#             return JsonResponse({'status': 'success', 'message': 'Doctor added successfully'}, status=201)
#         else:
#             return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

#     return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)



# @login_required(login_url='login_admin')
# def update_doctor(request, doctor_id):

#     if request.method == 'POST':

#         instance = doctor.objects.get(id=doctor_id)

#         print('-------------------')
#         print('-------------------')
#         print('-------------------')
#         print(instance.user)

#         updated_request = request.POST.copy()
#         updated_request.update({'user': instance.user})

#         forms = doctor_Form(updated_request, request.FILES, instance=instance)

#         print(forms.instance.user)

#         if forms.is_valid():
#             forms.save()
#             return redirect('list_doctor')
#         else:
#             print(forms.errors)

#     else:

#         instance = doctor.objects.get(id=doctor_id)
#         forms = doctor_Form(instance=instance)

#         context = {
#             'form': forms
#         }
#         return render(request, 'add_doctor.html', context)



from django.http import JsonResponse



@login_required(login_url='login_admin')
@user_passes_test(lambda u: u.is_superuser, login_url='login_admin')
def add_coupon(request):

    if request.method == 'POST':

        forms = coupon_Form(request.POST, request.FILES)

        if forms.is_valid():
            forms.save()
            messages.success(request, 'Coupon/Offer added successfully!')
            return redirect('list_coupon')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_coupon.html', context)

    else:

        forms = coupon_Form()

        context = {
            'form': forms
        }
        return render(request, 'add_coupon.html', context)



@login_required(login_url='login_admin')
@user_passes_test(lambda u: u.is_superuser, login_url='login_admin')
def update_coupon(request, coupon_id):

    if request.method == 'POST':

        instance = coupon.objects.get(id=coupon_id)

        forms = coupon_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            messages.success(request, 'Coupon/Offer updated successfully!')
            return redirect('list_coupon')
        else:
            print(forms.errors)

    else:

        instance = coupon.objects.get(id=coupon_id)
        forms = coupon_Form(instance=instance)

        context = {
            'form': forms
        }
        return render(request, 'add_coupon.html', context)



@login_required(login_url='login_admin')
@user_passes_test(lambda u: u.is_superuser, login_url='login_admin')
def delete_coupon(request, coupon_id):

    coupon.objects.get(id=coupon_id).delete()
    messages.success(request, 'Coupon/Offer deleted successfully!')

    return HttpResponseRedirect(reverse('list_coupon'))


@login_required(login_url='login_admin')
@user_passes_test(lambda u: u.is_superuser, login_url='login_admin')
def list_coupon(request):

    data = coupon.objects.all().order_by('-id')
    context = {
        'data': data
    }
    return render(request, 'list_coupon.html', context)


from django.http import JsonResponse
from .filters import *

class get_coupon(ListAPIView):
    queryset = coupon.objects.all().order_by('-id')
    serializer_class = coupon_serializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = couponFilter  # enables filtering on all fields (excluding image)



@login_required(login_url='login_admin')
def add_event(request):

    if request.method == 'POST':

        forms = event_Form(request.POST, request.FILES)

        if forms.is_valid():
            event_obj = forms.save()
            
            # Handle multiple gallery images
            from .models import EventImage
            gallery_images = request.FILES.getlist('gallery_images')
            for img in gallery_images:
                EventImage.objects.create(event=event_obj, image=img)
            
            return redirect('list_event')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_event.html', context)

    else:

        forms = event_Form()

        context = {
            'form': forms
        }
        return render(request, 'add_event.html', context)



@login_required(login_url='login_admin')
def update_event(request, event_id):

    if request.method == 'POST':

        instance = event.objects.get(id=event_id)

        forms = event_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            event_obj = forms.save()
            
            # Handle multiple gallery images
            from .models import EventImage
            gallery_images = request.FILES.getlist('gallery_images')
            for img in gallery_images:
                EventImage.objects.create(event=event_obj, image=img)
            
            return redirect('list_event')
        else:
            print(forms.errors)
            context = {
                'form': forms,
                'existing_images': instance.gallery_images.all() if instance else None,
            }
            return render(request, 'add_event.html', context)

    else:

        instance = event.objects.get(id=event_id)
        forms = event_Form(instance=instance)

        context = {
            'form': forms,
            'existing_images': instance.gallery_images.all() if instance else None,
        }
        return render(request, 'add_event.html', context)



@login_required(login_url='login_admin')
def delete_event_image(request, image_id):
    """Delete a specific event gallery image"""
    try:
        from .models import EventImage
        image_obj = EventImage.objects.get(id=image_id)
        event_id = image_obj.event.id
        image_obj.delete()
        from django.contrib import messages
        messages.success(request, "Image deleted successfully.")
        return redirect('update_event', event_id=event_id)
    except EventImage.DoesNotExist:
        from django.contrib import messages
        messages.error(request, "Image not found.")
        return redirect('list_event')


@login_required(login_url='login_admin')
def delete_event(request, event_id):

    event.objects.get(id=event_id).delete()

    return HttpResponseRedirect(reverse('list_event'))


@login_required(login_url='login_admin')
def list_event(request):

    data = event.objects.all().order_by('-id')
    context = {
        'data': data
    }
    return render(request, 'list_event.html', context)


from django.http import JsonResponse

class get_event(ListAPIView):
    queryset = event.objects.all().order_by('-id')
    serializer_class = event_serializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = EventFilter  # enables filtering on all fields


    def get_queryset(self):
        return event.objects.filter(start_date__gte=now()).order_by('start_date')


def add_testimonials(request):

    if request.method == "POST":

        forms = testimonials_Form(request.POST, request.FILES)

        if forms.is_valid():
            forms.save()
            return redirect('list_testimonials')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_testimonials.html', context)

    else:

        # create first row using admin then editing only



        return render(request, 'add_testimonials.html', { 'form' : testimonials_Form()})

def update_testimonials(request, testimonials_id):

    instance = testimonials.objects.get(id = testimonials_id)

    if request.method == "POST":

        forms = testimonials_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_testimonials')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_testimonials.html', context)


    else:

        # create first row using admin then editing only

        forms = testimonials_Form(instance=instance)

        context = {
            'form': forms
        }

        return render(request, 'add_testimonials.html', context)


def list_testimonials(request):

    data = testimonials.objects.all().order_by('-id')

    return render(request, 'list_testimonials.html', {'data' : data})


def delete_testimonials(request, testimonials_id):

    data = testimonials.objects.get(id = testimonials_id).delete()

    return redirect('list_testimonials')



from django.views import View


class get_testimonials(ListAPIView):
    queryset = testimonials.objects.all().order_by('-id')
    serializer_class = testimonials_serializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TestimonialsFilter  # enables filtering on all fields


def add_city(request):

    if request.method == "POST":

        forms = city_Form(request.POST, request.FILES)

        if forms.is_valid():
            forms.save()
            return redirect('list_city')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_city.html', context)

    else:

        # create first row using admin then editing only



        return render(request, 'add_city.html', { 'form' : city_Form()})

def update_city(request, city_id):

    instance = city.objects.get(id = city_id)

    if request.method == "POST":

        forms = city_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_city')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_city.html', context)


    else:

        # create first row using admin then editing only

        forms = city_Form(instance=instance)

        context = {
            'form': forms
        }

        return render(request, 'add_city.html', context)


def list_city(request):

    data = city.objects.all().order_by('-id')

    return render(request, 'list_city.html', {'data' : data})


def delete_city(request, city_id):

    data = city.objects.get(id = city_id).delete()

    return redirect('list_city')



from django.views import View


class get_city(ListAPIView):
    queryset = city.objects.all().order_by('-id')
    serializer_class = city_serializer



def add_amenity(request):

    if request.method == "POST":

        forms = amenity_Form(request.POST, request.FILES)

        if forms.is_valid():
            forms.save()
            return redirect('list_amenity')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_amenity.html', context)


    else:

        # create first row using admin then editing only



        return render(request, 'add_amenity.html', { 'form' : amenity_Form()})

def update_amenity(request, amenity_id):

    instance = amenity.objects.get(id = amenity_id)

    if request.method == "POST":

        forms = amenity_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_amenity')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_amenity.html', context)

    else:

        # create first row using admin then editing only

        forms = amenity_Form(instance=instance)

        context = {
                'form': forms
            }

        return render(request, 'add_amenity.html', context)


def list_amenity(request):

    data = amenity.objects.all().order_by('-id')

    return render(request, 'list_amenity.html', {'data' : data})


def delete_amenity(request, amenity_id):

    data = amenity.objects.get(id = amenity_id).delete()

    return redirect('list_amenity')


from django.views import View



class get_amenity(ListAPIView):
    queryset = amenity.objects.all()
    serializer_class = amenity_serializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AmenityFilter  # enables filtering on all fields (excluding image)

def add_property_type(request):

    if request.method == "POST":

        forms = property_type_Form(request.POST, request.FILES)

        if forms.is_valid():
            forms.save()
            return redirect('list_property_type')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_property_type.html', context)


    else:

        # create first row using admin then editing only



        return render(request, 'add_property_type.html', { 'form' : property_type_Form()})

def update_property_type(request, property_type_id):

    instance = property_type.objects.get(id = property_type_id)

    if request.method == "POST":

        forms = property_type_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_property_type')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_property_type.html', context)

    else:

        # create first row using admin then editing only

        forms = property_type_Form(instance=instance)

        context = {
                'form': forms
            }

        return render(request, 'add_property_type.html', context)


def list_property_type(request):

    data = property_type.objects.all().order_by('-id')

    return render(request, 'list_property_type.html', {'data' : data})


def delete_property_type(request, property_type_id):

    data = property_type.objects.get(id = property_type_id).delete()

    return redirect('list_property_type')


from django.views import View



class get_property_type(ListAPIView):
    queryset = property_type.objects.all().order_by('-id')
    serializer_class = property_type_serializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PropertyTypeFilter  # enables filtering on all fields

def add_villa_amenity(request):

    if request.method == "POST":

        forms = villa_amenity_Form(request.POST, request.FILES)
        if forms.is_valid():
            forms.save()
            return redirect('list_villa_amenity')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_villa_amenity.html', context)


    else:

        # create first row using admin then editing only



        return render(request, 'add_villa_amenity.html', { 'form' : villa_amenity_Form()})
def update_villa_amenity(request, villa_amenity_id):

    instance = villa_amenity.objects.get(id = villa_amenity_id)

    if request.method == "POST":

        forms = villa_amenity_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_villa_amenity')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_villa_amenity.html', context)

    else:

        # create first row using admin then editing only

        forms = villa_amenity_Form(instance=instance)

        context = {
                'form': forms
            }

        return render(request, 'add_villa_amenity.html', context)


def list_villa_amenity(request):
    data = villa_amenity.objects.all().order_by('-id')

    return render(request, 'list_villa_amenity.html', {'data' : data})


def delete_villa_amenity(request, villa_amenity_id):

    data = villa_amenity.objects.get(id = villa_amenity_id).delete()

    return redirect('list_villa_amenity')


from django.views import View



class get_villa_amenity(ListAPIView):
    queryset = villa_amenity.objects.all().order_by('-id')
    serializer_class = villa_amenity_serializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = VillaAmenityFilter  # enables filtering on all fields

def add_villa_type(request):

    if request.method == "POST":

        forms = villa_type_Form(request.POST, request.FILES)
        
        if forms.is_valid():
            forms.save()
            return redirect('list_villa_type')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_villa_type.html', context)


    else:

        # create first row using admin then editing only



        return render(request, 'add_villa_type.html', { 'form' : villa_type_Form()})

def update_villa_type(request, villa_type_id):

    instance = villa_type.objects.get(id = villa_type_id)
    if request.method == "POST":

        forms = villa_type_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_villa_type')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_villa_type.html', context)

    else:

        # create first row using admin then editing only

        forms = villa_type_Form(instance=instance)

        context = {
                'form': forms
            }

        return render(request, 'add_villa_type.html', context)


def list_villa_type(request):
    data = villa_type.objects.all().order_by('-id')

    return render(request, 'list_villa_type.html', {'data' : data})


def delete_villa_type(request, villa_type_id):

    data = villa_type.objects.get(id = villa_type_id).delete()

    return redirect('list_villa_type')

from django.views import View



class get_villa_type(ListAPIView):
    queryset = villa_type.objects.all().order_by('-id')
    serializer_class = villa_type_serializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = VillaTypeFilter  # enables filtering on all fields



from rest_framework.response import Response

from rest_framework.views import APIView

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import JSONParser



class customer_address_ViewSet(ModelViewSet):

    permission_classes = [IsCustomer]

    serializer_class = customer_address_serializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsCustomer]  # Or use IsAuthenticated if needed

    def get_queryset(self):
        return customer_address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



def update_customer_address(request, customer_address_id):

    instance = customer_address.objects.get(id = customer_address_id)

    if request.method == "POST":

        forms = customer_address_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_customer_address')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }
            return render(request, 'add_customer_address.html', context)

    else:

        # create first row using admin then editing only

        forms = customer_address_Form(instance=instance)

        context = {
                'form': forms
            }

        return render(request, 'add_customer_address.html', context)


def list_customer_address(request):

    data = customer_address.objects.all().order_by('-id')

    return render(request, 'list_customer_address.html', {'data' : data})


def delete_customer_address(request, customer_address_id):

    data = customer_address.objects.get(id = customer_address_id).delete()

    return redirect('list_customer_address')


from django.views import View



class get_customer_address(ListAPIView):
    queryset = customer_address.objects.all().order_by('-id')
    serializer_class = customer_address_serializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CustomerAddressFilter  # enables filtering on all fields

    def get_queryset(self):
        return customer_address.objects.filter(user=self.request.user)



def add_home_banner(request):

    if request.method == "POST":

        forms = home_banner_Form(request.POST, request.FILES)

        if forms.is_valid():
            forms.save()
            return redirect('list_home_banner')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }

            return render(request, 'add_home_banner.html', context)

    else:

        # create first row using admin then editing only



        return render(request, 'add_home_banner.html', { 'form' : home_banner_Form()})

def update_home_banner(request, home_banner_id):

    instance = home_banner.objects.get(id = home_banner_id)

    if request.method == "POST":


        instance = home_banner.objects.get(id=home_banner_id)

        forms = home_banner_Form(request.POST, request.FILES, instance=instance)

        if forms.is_valid():
            forms.save()
            return redirect('list_home_banner')
        else:
            print(forms.errors)
            context = {
                'form': forms
            }

            return render(request, 'add_home_banner.html', context)


    else:

        # create first row using admin then editing only

        forms = home_banner_Form(instance=instance)

        context = {
            'form': forms
        }

        return render(request, 'add_home_banner.html', context)


def list_home_banner(request):

    data = home_banner.objects.all().order_by('-id')

    return render(request, 'list_home_banner.html', {'data' : data})

def list_payments(request):

    if request.user.is_superuser:

        data = PaymentTransaction.objects.all().order_by('-id')
    else:


        data = PaymentTransaction.objects.filter(booking__hotel__user = request.user).order_by('-id')


    return render(request, 'list_payments.html', {'data' : data})


def delete_home_banner(request, home_banner_id):

    data = home_banner.objects.get(id = home_banner_id).delete()

    return redirect('list_home_banner')


from django.views import View

def get_home_banner(request):

    filtered_qs = home_bannerFilter(request.GET, queryset=home_banner.objects.all()).qs

    serialized_data = HomeBannerSerializer(filtered_qs, many=True, context={'request': request}).data
    return JsonResponse({"data": serialized_data}, status=200)



from customer.models import *
from django.db.models import Max


@login_required(login_url='login_admin')
def list_support_tickets(request):
    data = SupportTicket.objects.annotate(
        last_msg_time=Max('messages__created_at')
    ).order_by('-created_at')
    return render(request, 'support_chat.html', {'data': data})


@login_required(login_url='login_admin')
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    messages = ticket.messages.all().order_by('created_at')

    # Annotate all tickets with their last message time
    data = SupportTicket.objects.annotate(
        last_msg_time=Max('messages__created_at')
    ).order_by('-created_at')

    if request.method == "POST":
        msg = request.POST.get('message')
        if msg:
            TicketMessage.objects.create(ticket=ticket, sender=request.user, message=msg)
            return redirect('ticket_detail', ticket_id=ticket_id)

    return render(request, 'support_chat.html', {
        'ticket': ticket,
        'messages': messages,
        'data': data,
        'active_id': ticket.id
    })