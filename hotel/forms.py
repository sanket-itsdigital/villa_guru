from django import forms
from .models import *
from masters.models import *

class hotel_Form(forms.ModelForm):
   
    amenities = forms.ModelMultipleChoiceField(
        queryset=amenity.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select d-none',
        }),
        required=False
    )

    class Meta:
        model = hotel
        fields = '__all__'
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Villa Name"}),
            'category': forms.Select(attrs={'class': 'form-control', 'placeholder': "Category (e.g. Budget)"}),
            'no_of_rooms': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': "Number of Villa"}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': "Address"}),
            'city': forms.Select(attrs={'class': 'form-control select2'}),
            'star_rating': forms.NumberInput(attrs={'class': 'form-control'}),
            'overall_rating': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'pincode': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': "Pincode"}),
            'profit_margin': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
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
            self.fields.pop('is_active', None)  # hide is_active from vendors
            self.fields.pop('star_rating', None)  # hide is_active from vendors



class hotel_rooms_Form(forms.ModelForm):

    room_amenities = forms.ModelMultipleChoiceField(
    queryset=room_amenity.objects.all(),
    widget=forms.SelectMultiple(attrs={
        'class': 'form-select select2',  # important class!
        'id': 'id_room_amenities'
    }),
        required=False
    )

    class Meta:
        model = hotel_rooms
        fields = '__all__'
        widgets = {
            'hotel': forms.Select(attrs={'class': 'form-control'}),
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


