from django import forms
from .models import *
from masters.models import *
from decimal import Decimal

class villa_Form(forms.ModelForm):
   
    amenities = forms.ModelMultipleChoiceField(
        queryset=amenity.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select d-none',
        }),
        required=False
    )

    class Meta:
        model = villa
        fields = '__all__'
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Villa Name"}),
            'category': forms.Select(attrs={'class': 'form-control', 'placeholder': "Category (e.g. Budget)"}),
            'no_of_rooms': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': "Number of Villa"}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': "Address"}),
            'property_type': forms.Select(attrs={'class': 'form-control select2'}),
            'city': forms.Select(attrs={'class': 'form-control select2'}),
            'star_rating': forms.NumberInput(attrs={'class': 'form-control'}),
            'overall_rating': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'villa_star_facility': forms.Select(attrs={'class': 'form-control'}),
            'pincode': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': "Pincode"}),
            'profit_margin': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'markup_percentage': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01', 
                'min': '0',
                'max': '100',
                'placeholder': 'Custom markup % (e.g., 10 for 10%). Leave empty to use system-wide markup.'
            }),
            'price_per_night': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Villa price per night (for whole villa booking)'}),
            'weekend_percentage': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01', 
                'min': '0',
                'max': '100',
                'placeholder': 'Weekend price increase % (e.g., 25 for 25% increase on weekends)'
            }),
            'main_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': "Description", 'style': "padding: 10px"}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'go_live': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_recommended': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

            # GST Fields
            'gst_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 29ABCDE1234F2Z5'}),
            'gst_certificate': forms.ClearableFileInput(attrs={'class': 'form-control'}),

            # PAN Field
            'pan_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PAN Number'}),
            'landmark': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Landmark"}),

            # Bank Fields
            'account_holder_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Account Holder Name"}),
            'account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Account Number"}),
            'ifsc_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "IFSC Code"}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Bank Name"}),
            'bank_document': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # pop user from kwargs
        super().__init__(*args, **kwargs)

        if user and not user.is_superuser:
            self.fields.pop('profit_margin', None)
            self.fields.pop('markup_percentage', None)  # hide markup_percentage from vendors
            self.fields.pop('is_active', None)  # hide is_active from vendors
            self.fields.pop('star_rating', None)  # hide is_active from vendors
            
            # Check if villa has bookings - if yes, disable price_per_night for vendors
            if self.instance and self.instance.pk:
                from customer.models import VillaBooking
                has_bookings = VillaBooking.objects.filter(villa=self.instance).exists()
                
                if has_bookings and 'price_per_night' in self.fields:
                    # Make field readonly (not disabled, so value is submitted) and add styling
                    self.fields['price_per_night'].widget.attrs['readonly'] = True
                    self.fields['price_per_night'].widget.attrs['class'] = self.fields['price_per_night'].widget.attrs.get('class', '') + ' bg-light'
                    self.fields['price_per_night'].help_text = '⚠️ Price cannot be changed because this villa has existing bookings. Please contact admin if you need to update the price.'



class villa_rooms_Form(forms.ModelForm):

    villa_amenities = forms.ModelMultipleChoiceField(
    queryset=villa_amenity.objects.all(),
    widget=forms.SelectMultiple(attrs={
        'class': 'form-select select2',  # important class!
        'id': 'id_villa_amenities'
    }),
        required=False
    )

    class Meta:
        model = villa_rooms
        fields = '__all__'
        widgets = {
            'villa': forms.Select(attrs={'class': 'form-control'}),
            'room_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.Select(attrs={'class': 'form-control'}),  # it's a choice field
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'main_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'price_per_night': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_guest_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'refundable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'meals_included': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'bed_type': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.TextInput(attrs={'class': 'form-control'}),
            'view': forms.TextInput(attrs={'class': 'form-control'}),
        }


class VillaPricingForm(forms.ModelForm):
    class Meta:
        model = VillaPricing
        fields = ['date', 'price_per_night']
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'price_per_night': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Enter price per night',
                'required': True
            }),
        }


