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
        fields = ['name', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'id': 'name'
            }),
            'logo': forms.ClearableFileInput(attrs={
                'class': 'form-control', 'id': 'logo', 'accept': 'image/*'
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
        fields = ['name', 'amenities']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'id': 'name',
                'placeholder': 'e.g., Standard Room, Deluxe Room, Suite'
            }),
            'amenities': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show amenities that are available
        if 'amenities' in self.fields:
            self.fields['amenities'].queryset = villa_amenity.objects.all().order_by('name')
            self.fields['amenities'].required = False
            self.fields['amenities'].help_text = "Select the amenities that will be available for this room type. These amenities will be automatically assigned when you create rooms using this room type."
            # Style the checkboxes better
            self.fields['amenities'].widget.attrs.update({
                'class': 'form-check-input',
                'style': 'margin-right: 5px;'
            })
        
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
        fields = ['name', 'feature_image', 'description', 'itinerary', 'amount', 'location', 'start_date', 'end_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'name'}),
            'description': forms.Textarea(attrs={'class': 'form-control description-box', 'id': 'description', 'rows': 5}),
            'itinerary': forms.Textarea(attrs={'class': 'form-control description-box', 'id': 'itinerary', 'rows': 5, 'placeholder': 'Enter event itinerary/schedule'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'id': 'amount', 'step': '0.01', 'min': '0', 'placeholder': '0.00'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'id': 'location', 'placeholder': 'Enter event location'}),
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
    
    category = forms.ChoiceField(
        choices=home_banner.CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        initial='top'
    )

    class Meta:
        model = home_banner
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }