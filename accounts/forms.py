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
        fields = ['purpose', 'event_name', 'venue', 'description', 'addon_equipment', 'document', 'start_time', 'end_time']
        
        widgets = {
            'purpose': forms.Select(attrs={'class': 'form-control'}),
            'event_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Math Study Group'}),
            'venue': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Details about the event...'}),
            'addon_equipment': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2, 
                'placeholder': 'Need extras? List them here (e.g. 1x Microphone, 2x Whiteboard Markers)...'
            }),
            'document': forms.FileInput(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super(BookingForm, self).__init__(*args, **kwargs)
        
        # Customizing the Dropdown Text to show "Venue Name (Location)"
        self.fields['venue'].label_from_instance = lambda obj: f"{obj.name} ({obj.location})"
