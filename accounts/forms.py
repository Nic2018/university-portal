from django import forms
from .models import Booking

# 1. Search Form (For finding venues)
class VenueSearchForm(forms.Form):
    query = forms.CharField(label='Search Venues', max_length=100, required=False, 
                            widget=forms.TextInput(attrs={'placeholder': 'Search by name or location...'}))

# 2. Booking Form (For creating a new event)
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['venue', 'event_name', 'description', 'start_time', 'end_time']
        
        # This makes the date/time inputs look like real pickers in the browser
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }