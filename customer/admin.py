from django.contrib import admin

# Register your models here.


from .models import *

admin.site.register(HotelBooking)
admin.site.register(SupportTicket)
admin.site.register(PaymentTransaction)