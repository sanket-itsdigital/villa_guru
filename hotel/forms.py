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
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Property Name"}),
            'category': forms.Select(attrs={'class': 'form-control', 'placeholder': "Category (e.g. Budget)"}),
            'no_of_rooms': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': "Number of Villa"}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': "Address"}),
            'property_type': forms.Select(attrs={'class': 'form-control select2'}),
            'city': forms.Select(attrs={'class': 'form-control select2'}),
            'star_rating': forms.NumberInput(attrs={'class': 'form-control'}),
            'overall_rating': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'villa_star_facility': forms.Select(attrs={'class': 'form-control'}),
            'mrp': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Maximum Retail Price (MRP)'}),
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
            'about': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': "About the property - detailed information", 'style': "padding: 10px"}),
            'specialties': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': "Specialties - unique features and selling points", 'style': "padding: 10px"}),
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
            'price_per_night': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'max_guest_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'room_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'step': '1'}),
            'refundable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'meals_included': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'bed_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 1 Queen Bed + 1 Double Bed'}),
            'capacity': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2 Adults, 1 Child'}),
            'view': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Beach View, Garden View'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Ensure instance is set (for new forms, Django should create one, but ensure it exists)
        if self.instance is None:
            from .models import villa_rooms
            self.instance = villa_rooms()
        
        # Make villa field required with help text
        self.fields['villa'].required = True
        self.fields['price_per_night'].help_text = 'Enter the price per night for this room type.'
        self.fields['room_count'].help_text = 'Number of physical rooms of this type available in the property. Each room type can only be added once per property.'
        self.fields['room_count'].required = True
        self.fields['room_count'].min_value = 1
        
        # Filter room types based on user
        if user and user.is_service_provider and not user.is_superuser:
            # Vendor: show only their own room types + system-wide room types (user=None)
            from masters.models import room_type
            from django.db.models import Q
            self.fields['room_type'].queryset = room_type.objects.filter(
                Q(user=user) | Q(user__isnull=True)
            )
            self.fields['room_type'].help_text = 'Select the type of room. You can create your own room types in Room Type Management. Amenities from the selected room type will be pre-selected below.'
            
            # Add JavaScript to auto-populate amenities when room_type changes
            self.fields['room_type'].widget.attrs['onchange'] = 'updateAmenitiesFromRoomType(this)'
        else:
            # Admin: show all room types
            self.fields['room_type'].help_text = 'Select the type of room (e.g., Standard, Deluxe, Suite).'
    
    def clean(self):
        cleaned_data = super().clean()
        villa = cleaned_data.get('villa')
        room_type = cleaned_data.get('room_type')
        
        if villa and room_type:
            # Check if this room_type already exists for this villa (excluding current instance)
            from .models import villa_rooms
            existing = villa_rooms.objects.filter(villa=villa, room_type=room_type)
            
            # If updating, exclude current instance
            # self.instance is set by ModelForm, so we can safely check it
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise forms.ValidationError({
                    'room_type': f'This room type is already assigned to {villa.name}. Each room type can only be used once per property. Please edit the existing entry or choose a different room type.'
                })
        
        return cleaned_data


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


