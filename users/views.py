from email import message
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


from .forms import *


# def login_page(request):
#     forms = LoginForm()
#     if request.method == 'POST':
#         forms = LoginForm(request.POST)
#         if forms.is_valid():
#             username = forms.cleaned_data['username']
#             password = forms.cleaned_data['password']
#             print(username)
#             print(password)
#             user = authenticate(username=username, password=password)
#             if user:
#                 login(request, user)

#                 if user.is_doctor:
#                     print('---------------------------------')
#                     print('---------------------------------')
#                     print('---------------------------------')
#                 return redirect('dashboard')
#             else:
#                 messages.error(request, 'wrong username password')
#     context = {'form': forms}
#     return render(request, 'adminLogin.html', context)

from firebase_admin import auth as firebase_auth
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import  User  # Your custom user model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class SignupView(APIView):
    @swagger_auto_schema(
        operation_description="Register a new user with Firebase authentication",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['idToken', 'user_type'],
            properties={
                'idToken': openapi.Schema(type=openapi.TYPE_STRING, description='Firebase ID token'),
                'user_type': openapi.Schema(type=openapi.TYPE_STRING, enum=['customer', 'doctor', 'daycare', 'service_provider'], description='User type'),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='User full name'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='User email'),
            },
        ),
        responses={
            200: openapi.Response(
                description='Registration successful',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            400: openapi.Response(description='Bad request'),
        }
    )
    def post(self, request):
        id_token = request.data.get("idToken")
        user_type = request.data.get("user_type")
        name = request.data.get("name")
        email = request.data.get("email")

        if not id_token or not user_type:
            return Response({"error": "idToken and user_type are required"}, status=400)

        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
            mobile = decoded_token.get("phone_number")
            uid = decoded_token.get("uid")

            if not mobile:
                return Response({"error": "Phone number not found in Firebase token"}, status=400)

            # Role flags
            role_flags = {
                "is_customer": False,
                "is_doctor": False,
                "is_daycare": False,
                "is_service_provider": False
            }

            if f"is_{user_type}" not in role_flags:
                return Response({"error": "Invalid user_type"}, status=400)

            user = User.objects.filter(mobile=mobile).first()
            created = False

            if user:
                # Already exists – check role
                existing_roles = [key for key, value in {
                    "customer": user.is_customer,
                    "doctor": user.is_doctor,
                    "daycare": user.is_daycare,
                    "service_provider": user.is_service_provider
                }.items() if value]

                if existing_roles and user_type not in existing_roles:
                    return Response({
                        "error": f"This number is already registered as a {existing_roles[0]}. Cannot register again as {user_type}."
                    }, status=400)

                if user.firebase_uid != uid:
                    user.firebase_uid = uid
                    user.save()

            else:
                role_flags[f"is_{user_type}"] = True

                # Ensure email is unique
                if email and User.objects.filter(email=email).exists():
                    return Response({"error": "This email is already in use."}, status=400)

                user = User.objects.create(
                    mobile=mobile,
                    firebase_uid=uid,
                    first_name=name or "",
                    email=email or decoded_token.get("email", ""),
                    **role_flags
                )
                created = True

            # Create wallet if not customer
            wallet_amount = None
           
              
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "mobile": user.mobile,
                    "email": user.email,
                    "name": f"{user.first_name or ''} {user.last_name or ''}".strip(),
                    "user_type": (
                        "doctor" if user.is_doctor else
                        "daycare" if user.is_daycare else
                        "customer" if user.is_customer else
                        "service_provider" if user.is_service_provider else
                        "unknown"
                    ),
                    "created": created
                }
            })

        except Exception as e:
            return Response({"error": str(e)}, status=400)



from .serializer import *



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from firebase_admin import auth as firebase_auth
from django.contrib.auth import get_user_model



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from firebase_admin import auth as firebase_auth
from django.contrib.auth import get_user_model


User = get_user_model()


class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Login user with Firebase authentication",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['idToken'],
            properties={
                'idToken': openapi.Schema(type=openapi.TYPE_STRING, description='Firebase ID token'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            200: openapi.Response(description='Login successful'),
            400: openapi.Response(description='Bad request'),
        }
    )
    def post(self, request):
        id_token = request.data.get("idToken")
        print('------------------------------------')

        if not id_token:
            return Response({"error": "idToken is required"}, status=400)

        try:
            print('-----------------1-------------------')

            decoded_token = firebase_auth.verify_id_token(id_token)
            mobile = decoded_token.get("phone_number")
            uid = decoded_token.get("uid")
            print('-----------------2-------------------')
            print(mobile)

            if not mobile:
                return Response({"error": "Phone number not found in token"}, status=400)

            # Get or create user
            user, created = User.objects.get_or_create(
                mobile=mobile,
                is_customer=True,
                defaults={'firebase_uid': uid}
            )
            print('--------------3----------------------')

            # Ensure active
            if not user.is_active:
                user.is_active = True
                user.save()
                print('-------------31-----------------------')

            # Update firebase UID if changed
            if user.firebase_uid != uid:
                user.firebase_uid = uid
                user.save()
                print('--------------41----------------------')

            print('---------------4---------------------')

            # Optional fields from frontend
            optional_fields = ["email", "first_name", "last_name"]

            for field in optional_fields:
                if field in request.data:
                    value = request.data.get(field)

                    if field == "email" and value:
                        # Ensure unique email (skip if already taken)
                        if User.objects.exclude(id=user.id).filter(email=value).exists():
                            print(f"Email {value} already in use, skipping update")
                            continue  # skip updating email
                    setattr(user, field, value)

            user.save()
            print('------------------5------------------')

            # JWT tokens
            refresh = RefreshToken.for_user(user)
            user_data = UserProfileSerializer(user).data

            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "mobile": user.mobile,
                    "is_customer": user.is_customer,
                    "created": created
                },
                "user_details": user_data
            })

        except Exception as e:
            print("Firebase auth error:", e)
            return Response({"error": "Invalid or expired Firebase token."}, status=400)


from .permissions import *


class UsergetView(APIView):
    permission_classes = [IsCustomer]

    def get(self, request):
        user = request.user
        return Response({
            "name": user.first_name,
            "email": user.email,
        })

class UserUpdateView(APIView):
    permission_classes = [IsCustomer]

    def put(self, request):
        user = request.user
        name = request.data.get("name")
        email = request.data.get("email")

        updated = False

        if name:
            user.first_name = name
            updated = True

        if email:
            user.email = email
            updated = True

        if updated:
            user.save()
            return Response({"message": "Profile updated successfully."})
        else:
            return Response({"message": "No changes provided."}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    def post(self, request):
        id_token = request.data.get("idToken")
        new_password = request.data.get("new_password")

        if not id_token or not new_password:
            return Response({"error": "idToken and new_password are required"}, status=400)

        try:
            # Decode the token to get UID
            decoded = firebase_auth.verify_id_token(id_token)
            uid = decoded.get("uid")

            # Update Firebase password
            firebase_auth.update_user(uid, password=new_password)

            return Response({"message": "Password updated successfully."})

        except Exception as e:
            return Response({"error": str(e)}, status=400)
        



def login_admin(request):

    forms = LoginForm()
    if request.method == 'POST':
        forms = LoginForm(request.POST)
        if forms.is_valid():
            email = forms.cleaned_data['email']
            password = forms.cleaned_data['password']
            print(email)
            print(password)

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return render(request, 'adminLogin.html', {'error': 'Invalid email or password'})
            
            if user:
                if user.check_password(password):
                    if user.is_superuser:
                        login(request, user)
                        return redirect('dashboard')
                    else:
                        messages.error(request, 'You are not superuser')
                        context = {'form': forms}
                        return render(request, 'adminLogin.html', context)
                else:
                    return render(request, 'adminLogin.html', {'error': 'Invalid email or password'})

            else:
                messages.error(request, 'wrong username password')
    context = {'form': forms}
    return render(request, 'adminLogin.html', context)

import firebase_admin
from firebase_admin import auth
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import get_user_model
import json




def vendor_request(request):

    data = villa.objects.filter(is_active = False).select_related('user', 'city', 'property_type').prefetch_related('amenities', 'rooms')

    context = {
        'data' : data
    }

    return render(request, 'vendor_request_list.html', context)

from django.core.mail import send_mail
from django.http import HttpResponse

def send_test_email(request, subject, body, user_instance):
    send_mail(
        subject=subject,
        message=body,
        from_email='Rabbitstay221@gmail.com',
        recipient_list=[user_instance.email],  # send to user email
        fail_silently=False,
    )
    return HttpResponse("Email sent successfully!")


def activate_vendor_request(request, user_id):

    user_instance = User.objects.get(id = user_id)
    user_instance.is_active = True

    user_instance.save()

    villa_instance = villa.objects.get(user = user_instance)
    villa_instance.is_active = True

    villa_instance.save()

    msg =  'Hi, Your account is activated login and completed your profile' + str(villa_instance.id)

    send_test_email(request, 'Your account is actiated', msg, user_instance)

    return redirect('vendor_request')


from hotel.forms import villa_Form

def register_vendor(request):

    if request.method == 'POST':

        form = villa_Form(request.POST, request.FILES)  # ⬅️ Preserve submitted data

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not all([first_name, last_name, email, mobile, password, confirm_password]):
            print('----1----')
            context = { 
                'form': form, 
                'error': 'All fields are required.'
            }
            return render(request, 'hotel_registration_new.html', context)

        if password != confirm_password:
            print('----2----')
            context = { 
                'form': form, 
                'error': 'Passwords do not match.'
            }
            return render(request, 'hotel_registration_new.html', context)

        if User.objects.filter(email=email).exists():
            print('----3----')
            context = { 
                'form': form, 
                'error': 'Email already registered.'
            }
            return render(request, 'hotel_registration_new.html',  context)

        if User.objects.filter(mobile=mobile).exists():
            print('----4---')
            context = { 
                'form': form, 
                'error': 'Mobile number already registered.'
            }
            return render(request, 'hotel_registration_new.html',  context)

        try:
            # Create the user
            user = User.objects.create_user(
                email=email,
                mobile=mobile,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_service_provider=True,
                is_active=False
            )

            if not request.user.is_superuser:
                form.fields.pop('profit_margin')

            if form.is_valid():
                villa_obj = form.save(commit=False)
                if not request.user.is_superuser:
                    villa_obj.user = user  # auto-assign vendor user
                villa_obj.save()
                form.save_m2m()

                for img in request.FILES.getlist('image'):
                    VillaImage.objects.create(villa=villa_obj, image=img)

                return render(request, 'hotel_registration_succful.html')

            else:
                print(form.errors)
                context = { 'form': form }
                return render(request, 'hotel_registration_new.html', context)

        except Exception as e:
            print(f"Registration failed: {e}")
            user.delete()  # optional: rollback user if villa fails
            context = { 
                'form': form, 
                'error': 'Something went wrong during registration. Please try again.'
            }
            return render(request, 'hotel_registration_new.html', context)

    else:

    
        form = villa_Form()

        context = { 
                'form': form, 
        }

        return render(request, 'hotel_registration_new.html', context)


        

def login_vendor(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, 'Invalid email or password')
                return render(request, 'vendorLogin.html', {'form': form})

            if user.check_password(password):
                if not user.is_active:
                    messages.error(request, 'Your account verification is under process.')
                    return render(request, 'vendorLogin.html', {'form': form})

                if user.is_service_provider:
                    login(request, user)
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Access denied: not a service provider')
            else:
                messages.error(request, 'Invalid email or password')

    return render(request, 'vendorLogin.html', {'form': form})


from django.contrib.auth import views as auth_views

class MyPasswordResetView(auth_views.PasswordResetView):
    def get_email_subject(self):
        return "Reset Your Password"  # Static subject here

def login_staff(request):
   
    form = LoginForm(request.POST)

    if form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return render(request, 'stafflogin.html', {'form': form})

        if user.check_password(password):
            login(request, user)

            print('------------------')

            print(request.user)


            
            return redirect('dashboard')
           
        else:
            messages.error(request, "Invalid email or password.")
    
    return render(request, 'stafflogin.html')

# def resgister_page(request):

#     forms = registerForm()
#     if request.method == 'POST':
#         forms = registerForm(request.POST)
#         if forms.is_valid():
#             forms.save()
#             username = forms.cleaned_data['username']
#             password = forms.cleaned_data['password1']
#             user = authenticate(username=username, password=password)
#             if user:
                
#                 messages.error(request, 'user already exsist')
#                 return redirect('dashboard')
#             else:
#                 return redirect('resgister')
#         else:
#             print(forms.errors)
#     else:
#         print(forms.as_p)

#         context = {'form': forms}

#         return render(request, 'users/resgister.html', context)


def logout_page(request):
    logout(request)
    return redirect('login_admin')


def vendor_logout_page(request):
    logout(request)
    return redirect('login_vendor')

def staff_logout_page(request):
    logout(request)
    return redirect('login_staff')


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def customer_user_list(request):

    data = User.objects.filter(is_customer = True).order_by('-date_joined')

    paginator = Paginator(data, 30)  # Show 10 villas per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'user_list.html', { 'data' : page_obj})


def provider_user_list(request):

    data = User.objects.filter(is_service_provider=True).select_related('villa').order_by('-date_joined')

    paginator = Paginator(data, 30)  # Show 30 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'staff_list.djhtml', {'data': page_obj})


from customer.models import VillaBooking
from hotel.models import villa, VillaImage


def user_booking_history(request, user_id):

    data = VillaBooking.objects.filter(user__id = user_id)

    user_instance = User.objects.get(id = user_id)


    return render(request, 'user_booking_history.html', { 'data' : data, 'user_instance' : user_instance})



def hotel_booking_history(request, user_id):

    data = VillaBooking.objects.filter(villa__user__id = user_id)

    villa_instance = villa.objects.get(user__id = user_id)

    return render(request, 'hotel_booking_history.html', { 'data' : data, 'hotel_instance' : villa_instance})





from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import user_passes_test

def add_custom_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.groups.set(form.cleaned_data['groups'])
            return redirect('list_custom_user')
    else:
        form = UserForm()
    return render(request, 'add_custom_user.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def update_custom_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            user.groups.set(form.cleaned_data['groups'])
            return redirect('list_custom_user')
    else:
        form = UserForm(instance=user)
    return render(request, 'add_custom_user.html', {'form': form, 'update': True})



@user_passes_test(lambda u: u.is_superuser)
def delete_custom_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    
    return redirect('list_custom_user')


@user_passes_test(lambda u: u.is_superuser)
def list_custom_user(request):
    
    users = User.objects.filter(
        is_customer=False,
        is_service_provider=False
    ).order_by('-date_joined')

    paginator = Paginator(users, 30)  # Show 10 villas per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    

    return render(request, 'custom_user_list.html', { 'data' : page_obj})




from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from .serializer import UserProfileSerializer
from .models import User
from rest_framework.decorators import action


from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

class UserProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]  # 👈 necessary for photo uploads

    @action(detail=False, methods=['get', 'put'], url_path='me')
    def me(self, request):
        user = request.user

        if request.method == 'GET':
            serializer = UserProfileSerializer(user)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = UserProfileSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .forms import EmailChangeForm


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Password changed successfully.")
            return redirect('user_profile')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'change_password.html', {'form': form})


def change_email_request(request):
    if request.method == 'POST':
        form = EmailChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            new_email = form.cleaned_data['new_email']
            uid = urlsafe_base64_encode(force_bytes(request.user.pk))
            token = default_token_generator.make_token(request.user)
            link = request.build_absolute_uri(
                f"/users/verify-email/{uid}/{token}/?email={new_email}"
            )
            send_mail(
                subject="Confirm your new email address",
                message=f"Click to confirm your new email: {link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[new_email],
            )

            user_instance = request.user
            user_instance.email_verified = False
            user_instance.save()


            messages.success(request, "A verification email has been sent to your new address.")
            return redirect('user_profile')
    else:
        form = EmailChangeForm(user=request.user)
    return render(request, 'change_email.html', {'form': form})




def verify_email_change(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        new_email = request.GET.get('email')

        if default_token_generator.check_token(user, token):
            user.email = new_email
            user.email_verified = True
            user.save()
            messages.success(request, "Your email address has been updated.")
        else:
            messages.error(request, "Invalid or expired link.")

    except (User.DoesNotExist, ValueError, TypeError):
        messages.error(request, "Something went wrong.")
    
    return redirect('user_profile')


@login_required
def user_profile(request):
    from masters.models import SystemSettings
    from .forms import SystemSettingsForm
    
    system_settings = SystemSettings.get_settings()
    settings_form = None
    
    # Only show settings form to superusers
    if request.user.is_superuser:
        if request.method == 'POST' and 'update_markup' in request.POST:
            settings_form = SystemSettingsForm(request.POST, instance=system_settings)
            if settings_form.is_valid():
                settings_form.save()
                messages.success(request, f'Price markup percentage updated to {system_settings.price_markup_percentage}%')
                return redirect('user_profile')
        else:
            settings_form = SystemSettingsForm(instance=system_settings)
    
    return render(request, 'profile.html', {
        'user': request.user,
        'system_settings': system_settings,
        'settings_form': settings_form
    })

    
@login_required
def edit_user_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('user_profile')
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': form})



from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction, IntegrityError
import firebase_admin


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request):

    user = request.user

    try:
        with transaction.atomic():
            # Delete user from Firebase first
            if getattr(user, "firebase_uid", None):
                try:
                    auth.delete_user(user.firebase_uid)
                except Exception as e:
                    raise IntegrityError(f"Firebase deletion failed: {str(e)}")

            # Delete user from Django
            user.delete()

        return Response(
            {"detail": "Your account has been deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )

    except IntegrityError as e:
        return Response(
            {"detail": f"Account deletion failed: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST
        )
