from django.contrib import admin

# Register your models here.


from .models import *

admin.site.register(villa)
admin.site.register(villa_rooms)