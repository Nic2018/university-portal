from django import forms
from .models import Venue, Booking

class VenueSearchForm(forms.Form):
    query = forms.CharField(
        required=False, 
        label='Search',
        widget=forms.TextInput(attrs={'placeholder': 'Search venues...'})
    )

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        # UPDATED: Added 'purpose' and 'document' to the fields list
        fields = ['venue', 'purpose', 'event_name', 'description', 'start_time', 'end_time', 'document']
        
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            # You can add specific widgets here if needed, but the defaults usually work fine
        }

    def __init__(self, *args, **kwargs):
        super(BookingForm, self).__init__(*args, **kwargs)
        
        # --- Customizing the Dropdown Text ---
        # This shows "Venue Name (Location)" in the dropdown
        self.fields['venue'].label_from_instance = lambda obj: f"{obj.name} ({obj.location})"
        
        # --- Styling ---
        # Adds the 'form-control' class to all inputs for consistent design
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            
            
# NEW FORM WITH ADDON EQUIPMENT FIELD          
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        # Add 'addon_equipment' to the fields list
        fields = ['purpose', 'event_name', 'venue', 'description', 'addon_equipment', 'document', 'start_time', 'end_time']
        
        widgets = {
            # ... keep your existing widgets ...
            'event_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Math Study Group'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Details about the event...'}),
            
            # NEW WIDGET FOR ADD-ON EQUIPMENT
            'addon_equipment': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'Need extras? List them here (e.g. 1x Microphone, 2x Whiteboard Markers)...'
            }),
            
            'start_time': forms.TextInput(attrs={'class': 'datetime-picker'}),
            'end_time': forms.TextInput(attrs={'class': 'datetime-picker'}),
        }