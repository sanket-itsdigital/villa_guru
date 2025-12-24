from django.urls import path

from .views import *

from django.conf import settings
from django.conf.urls.static import static




from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'customer-address', customer_address_ViewSet, basename='test-booking')


urlpatterns = [


    # path('add-doctor/', add_doctor, name='add_doctor'),
    # path('add-doctor-json/', add_doctor_json, name='add_doctor_json'),
    # path('update-doctor/<doctor_id>', update_doctor, name='update_doctor'),

    path('add-coupon/', add_coupon, name='add_coupon'),
    path('update-coupon/<coupon_id>', update_coupon, name='update_coupon'),
    path('delete-coupon/<coupon_id>', delete_coupon, name='delete_coupon'),
    path('list-coupon/', list_coupon, name='list_coupon'),
    path('get-coupon/', get_coupon.as_view(), name='get_coupon'),

    path('add-event/', add_event, name='add_event'),
    path('update-event/<event_id>', update_event, name='update_event'),
    path('delete-event/<event_id>', delete_event, name='delete_event'),
    path('list-event/', list_event, name='list_event'),
    path('get-event/', get_event.as_view(), name='get_event'),

    path('add-testimonials/', add_testimonials, name='add_testimonials'),  # create or fetch list of admins
    path('update-testimonials/<testimonials_id>', update_testimonials, name='update_testimonials'),  # create or fetch list of admins
    path('list-testimonials/', list_testimonials, name='list_testimonials'),  # create or fetch list of admins
    path('delete-testimonials/<testimonials_id>', delete_testimonials, name='delete_testimonials'),  # create or fetch list of admins
    path('get-testimonials/', get_testimonials.as_view(), name='get_testimonials'), 

    path('add-city/', add_city, name='add_city'),  # create or fetch list of admins
    path('update-city/<city_id>', update_city, name='update_city'),  # create or fetch list of admins
    path('list-city/', list_city, name='list_city'),  # create or fetch list of admins
    path('delete-city/<city_id>', delete_city, name='delete_city'),  # create or fetch list of admins
    path('get-city/', get_city.as_view() , name='get_city '), 

    path('add-amenity/', add_amenity, name='add_amenity'),  # create or fetch list of admins
    path('update-amenity/<amenity_id>', update_amenity, name='update_amenity'),  # create or fetch list of admins
    path('list-amenity/', list_amenity, name='list_amenity'),  # create or fetch list of admins
    path('delete-amenity/<amenity_id>', delete_amenity, name='delete_amenity'),  # create or fetch list of admins
    path('get-amenity/', get_amenity.as_view() , name='get_amenity '), 

    path('add-property-type/', add_property_type, name='add_property_type'),  # create or fetch list of admins
    path('update-property-type/<property_type_id>', update_property_type, name='update_property_type'),  # create or fetch list of admins
    path('list-property-type/', list_property_type, name='list_property_type'),  # create or fetch list of admins
    path('delete-property-type/<property_type_id>', delete_property_type, name='delete_property_type'),  # create or fetch list of admins
    path('get-property-type/', get_property_type.as_view() , name='get_property_type '), 

    path('add-room_amenity/', add_room_amenity, name='add_room_amenity'),  # create or fetch list of admins
    path('update-room_amenity/<room_amenity_id>', update_room_amenity, name='update_room_amenity'),  # create or fetch list of admins
    path('list-room_amenity/', list_room_amenity, name='list_room_amenity'),  # create or fetch list of admins
    path('delete-room_amenity/<room_amenity_id>', delete_room_amenity, name='delete_room_amenity'),  # create or fetch list of admins
    path('get-room_amenity/', get_room_amenity.as_view() , name='get_room_amenity '), 
    
    path('add-room-type/', add_room_type, name='add_room_type'),  # create or fetch list of admins
    path('update-room-type/<room_type_id>', update_room_type, name='update_room_type'),  # create or fetch list of admins
    path('list-room-type/', list_room_type, name='list_room_type'),  # create or fetch list of admins
    path('delete-room-type/<room_type_id>', delete_room_type, name='delete_room_type'),  # create or fetch list of admins
    path('get-room-type/', get_room_type.as_view() , name='get_room_type '), 
    
  
    # path('add-customer-address/', add_customer_address.as_view(), name='add_customer_address'),  # create or fetch list of admins
    path('update-customer-address/<customer_address_id>', update_customer_address, name='update_customer_address'),  # create or fetch list of admins
    path('list-customer-address/', list_customer_address, name='list_customer_address'),  # create or fetch list of admins
    path('delete-customer-address/<customer_address_id>', delete_customer_address, name='delete_customer_address'),  # create or fetch list of admins
    # path('get-customer-address/', get_customer_address.as_view() , name='get_customer_address '), 

    
    path('add-home-banner/', add_home_banner, name='add_home_banner'),  # create or fetch list of admins
    path('update-home-banner/<home_banner_id>', update_home_banner, name='update_home_banner'),  # create or fetch list of admins
    path('list-home-banner/', list_home_banner, name='list_home_banner'),  # create or fetch list of admins
    path('delete-home-banner/<home_banner_id>', delete_home_banner, name='delete_home_banner'),  # create or fetch list of admins
    path('get-home-banner/', get_home_banner, name='get_home_banner'), 
    
    path('list-payments/', list_payments, name='list_payments'), 

    path('admin/support-tickets/', list_support_tickets, name='list_support_tickets'),
    path('admin/support-tickets/<int:ticket_id>/', ticket_detail, name='ticket_detail'),


]  + router.urls

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)