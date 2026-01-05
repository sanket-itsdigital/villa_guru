from django import forms

from .models import *
from django.contrib.admin.widgets import  AdminDateWidget, AdminTimeWidget, AdminSplitDateTime


class coupon_Form(forms.ModelForm):
    class Meta:
        model = coupon
        fields = '__all__'  # Include all fields
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Coupon Code'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Coupon Code'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'min_purchase': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }



class testimonials_Form(forms.ModelForm):
    class Meta:
        model = testimonials
        fields = '__all__'
        widgets = {
           
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'id': 'name'
            }),

            'rating': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
          
            'description': forms.TextInput(attrs={
                'class': 'form-control', 'id': 'price'
            }),

        }

        
class amenity_Form(forms.ModelForm):
    class Meta:
        model = amenity
        fields = '__all__'
        widgets = {
           
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'id': 'name'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control', 'id': 'image', 'accept': 'image/*'
            })

        }
        
class property_type_Form(forms.ModelForm):
    class Meta:
        model = property_type
        fields = '__all__'
        widgets = {
            'name': forms.Select(
                attrs={'class': 'form-control', 'id': 'name'}
            )
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set choices for the name field
        self.fields['name'].choices = property_type.PROPERTY_TYPE_CHOICES
        
class city_Form(forms.ModelForm):
    class Meta:
        model = city
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'id': 'name'
            }),
        }
        
        
class villa_amenity_Form(forms.ModelForm):
    class Meta:
        model = villa_amenity
        fields = '__all__'
        widgets = {
           
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'id': 'name'
            })

        }
        
class room_type_Form(forms.ModelForm):
    class Meta:
        model = room_type
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'id': 'name',
                'placeholder': 'e.g., Standard Room, Deluxe Room, Suite'
            }),
            'user': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # For admins: show user field to assign to specific vendor
        # For vendors: user field will be hidden and auto-assigned
        if 'user' in self.fields:
            from users.models import User
            self.fields['user'].queryset = User.objects.filter(is_service_provider=True)
            self.fields['user'].required = False
            self.fields['user'].help_text = "Leave empty for system-wide room type (admin only). For vendors, this is auto-assigned."
        
class villa_type_Form(forms.ModelForm):
    class Meta:
        model = villa_type
        fields = '__all__'
        widgets = {
           
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'id': 'name'
            })

        }

        

class event_Form(forms.ModelForm):
    class Meta:
        model = event
        fields = ['name', 'feature_image', 'description', 'itinerary', 'amount', 'start_date', 'end_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'name'}),
            'description': forms.Textarea(attrs={'class': 'form-control description-box', 'id': 'description', 'rows': 5}),
            'itinerary': forms.Textarea(attrs={'class': 'form-control description-box', 'id': 'itinerary', 'rows': 5, 'placeholder': 'Enter event itinerary/schedule'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'id': 'amount', 'step': '0.01', 'min': '0', 'placeholder': '0.00'}),
            'feature_image': forms.ClearableFileInput(attrs={'class': 'form-control', 'id': 'feature_image', 'accept': 'image/*'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local', 'id': 'start_date'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local', 'id': 'end_date'}),

        }


class customer_address_Form(forms.ModelForm):
    class Meta:
        model = customer_address
        fields = ['name', 'type', 'address', 'landmark', 'pin_code', 'city', 'state']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'landmark': forms.TextInput(attrs={'class': 'form-control'}),
            'pin_code': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
        }


class home_banner_Form(forms.ModelForm):

    is_for_web = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = home_banner
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'discription': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),

        }