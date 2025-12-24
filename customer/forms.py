from django import forms
from .models import HotelBooking

class HotelBookingStatusForm(forms.ModelForm):
    class Meta:
        model = HotelBooking
        fields = '__all__'

    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract user from the view
        super().__init__(*args, **kwargs)

        # Apply bootstrap class
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.disabled = True  # Disable everything by default

        # Always allow status to be editable
        self.fields['status'].disabled = False  

        # If user is not superuser → restrict status choices
        if user and not user.is_superuser:
            self.fields['status'].choices = [
                choice for choice in self.fields['status'].choices
                if choice[0] not in ['confirmed', 'cancelled']
            ]
        else:
            # ✅ If user *is* admin → allow editing payment fields too
            self.fields['payment_type'].disabled = False
            self.fields['payment_status'].disabled = False