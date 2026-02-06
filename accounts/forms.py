from django import forms
from .models import Venue, Booking, VenueSchedule

class VenueSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={'placeholder': 'Search venues...'})
    )

class BookingForm(forms.ModelForm):
    # Add time slot selection
    use_time_slot = forms.BooleanField(
        required=False,
        label='Use preset time slot',
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Booking
        fields = ['purpose', 'event_name', 'venue', 'description', 'addon_equipment', 'document', 'start_time', 'end_time', 'time_slot']

        widgets = {
            'purpose': forms.Select(attrs={'class': 'form-control'}),
            'event_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Math Study Group'}),
            'venue': forms.Select(attrs={'class': 'form-control', 'id': 'id_venue_select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Details about the event...'}),
            'addon_equipment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Need extras? List them here (e.g. 1x Microphone, 2x Whiteboard Markers)...'
            }),
            'document': forms.FileInput(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local', 'id': 'id_start_time'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local', 'id': 'id_end_time'}),
            'time_slot': forms.Select(attrs={'class': 'form-control', 'id': 'id_time_slot'}),
        }

    def __init__(self, *args, **kwargs):
        super(BookingForm, self).__init__(*args, **kwargs)

        # Customizing the Dropdown Text to show "Venue Name (Location)"
        self.fields['venue'].label_from_instance = lambda obj: f"{obj.name} ({obj.location})"

        # Make time_slot optional and populate with time slot options
        schedule = VenueSchedule.get_schedule()
        slots = schedule.get_time_slots()

        slot_choices = [('', '--- Select a time slot ---')]
        slot_choices.extend([(slot['display'], slot['display']) for slot in slots])

        self.fields['time_slot'].choices = slot_choices
        self.fields['time_slot'].required = False

