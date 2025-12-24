from django.contrib import admin

# Register your models here.


from .models import *

admin.site.register(hotel)
admin.site.register(hotel_rooms)