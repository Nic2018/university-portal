import qrcode
from io import BytesIO
from django.core.files import File
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

# 0. Global Schedule Configuration
class VenueSchedule(models.Model):
    """Global operating hours and time slot configuration for all venues"""
    open_hour = models.IntegerField(default=8, help_text="Opening hour (0-23)")
    close_hour = models.IntegerField(default=20, help_text="Closing hour (0-23)")
    slot_duration_minutes = models.IntegerField(default=60, help_text="Duration of each time slot in minutes")
    days_in_advance = models.IntegerField(default=30, help_text="Maximum days in advance for bookings")

    class Meta:
        verbose_name_plural = "Venue Schedule"

    def __str__(self):
        return f"Schedule: {self.open_hour}:00 - {self.close_hour}:00 ({self.slot_duration_minutes} min slots)"

    @classmethod
    def get_schedule(cls):
        """Get or create default schedule"""
        schedule, _ = cls.objects.get_or_create(pk=1)
        return schedule

    def get_time_slots(self):
        """Generate list of all available time slots for the day"""
        slots = []
        current_hour = self.open_hour
        current_minute = 0

        while True:
            end_hour = current_hour
            end_minute = current_minute + self.slot_duration_minutes

            if end_minute >= 60:
                end_hour += end_minute // 60
                end_minute = end_minute % 60

            if end_hour > self.close_hour:
                break

            slot_display = f"{current_hour:02d}:{current_minute:02d}-{end_hour:02d}:{end_minute:02d}"
            slots.append({
                'display': slot_display,
                'start': f"{current_hour:02d}:{current_minute:02d}",
                'end': f"{end_hour:02d}:{end_minute:02d}",
            })

            current_minute += self.slot_duration_minutes
            if current_minute >= 60:
                current_hour += current_minute // 60
                current_minute = current_minute % 60

        return slots

# 1. The Venue Table
class Venue(models.Model):
    name = models.CharField(max_length=200, help_text="e.g. Lecture Hall A")
    location = models.CharField(max_length=200, help_text="e.g. Block B, Level 2")
    capacity = models.IntegerField(help_text="How many people can fit?")
    equipment = models.CharField(max_length=200, blank=True, help_text="e.g. Projector, Wifi, AC")

    def __str__(self):
        return f"{self.name} ({self.location})"

    class Meta:
        ordering = ['name']

# 2. The Booking Table
class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    PURPOSE_CHOICES = [
        ('STUDY', 'Study'),
        ('EVENT', 'Event'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='bookings')
    
    purpose = models.CharField(max_length=10, choices=PURPOSE_CHOICES, default='STUDY')
    event_name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    
    document = models.FileField(upload_to='booking_docs/', blank=True, null=True)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Admin approval tracking
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_bookings')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    addon_equipment = models.TextField(blank=True, null=True, help_text="List any extra equipment needed (e.g., Extra Mic, Extension Cord).")
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    time_slot = models.CharField(max_length=20, blank=True, null=True, help_text="Selected time slot (e.g. 09:00-10:00)")

    def clean(self):
        """Validate booking times"""
        errors = {}
        if self.start_time is None:
            errors['start_time'] = 'Start time is required.'
        if self.end_time is None:
            errors['end_time'] = 'End time is required.'
        if errors:
            raise ValidationError(errors)

        if self.start_time >= self.end_time:
            raise ValidationError({'end_time': "End time must be after start time."})

        if self.start_time < timezone.now():
            raise ValidationError({'start_time': "Cannot book for past times."})

        # Check operating hours
        schedule = VenueSchedule.get_schedule()
        start_hour = self.start_time.hour
        end_hour = self.end_time.hour
        end_minute = self.end_time.minute

        if start_hour < schedule.open_hour or start_hour >= schedule.close_hour:
            raise ValidationError({'start_time': f"Start time must be between {schedule.open_hour}:00 and {schedule.close_hour}:00"})

        # Check end time: must not go past close hour (even by 1 minute)
        if end_hour > schedule.close_hour or (end_hour == schedule.close_hour and end_minute > 0):
            raise ValidationError({'end_time': f"End time must be before {schedule.close_hour}:00"})

        # Check for clashes with BOTH approved and pending bookings
        # This prevents users from creating multiple conflicting bookings
        clashing = Booking.objects.filter(
            venue=self.venue,
            status__in=['APPROVED', 'PENDING'],  # ← Check both statuses
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        )

        # Exclude current booking when editing
        if self.pk:
            clashing = clashing.exclude(pk=self.pk)

        if clashing.exists():
            # Get the first clashing booking's event name separately to avoid recursion
            first_clash = clashing.first()
            clash_name = first_clash.event_name if first_clash else "another booking"
            raise ValidationError(f"Time slot conflicts with existing booking: {clash_name}")

    def save(self, *args, **kwargs):
        # Generate QR code when status changes to APPROVED
        if self.status == 'APPROVED' and not self.qr_code:
            qr_data = f"ENTRY PASS\nID: {self.id}\nUser: {self.user.username}\nEvent: {self.event_name}\nVenue: {self.venue.name}\nTime: {self.start_time}"
            
            qr_img = qrcode.make(qr_data)
            canvas = BytesIO()
            qr_img.save(canvas, format='PNG')
            
            file_name = f"qr_booking_{self.id}.png"
            self.qr_code.save(file_name, File(canvas), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.event_name} - {self.status}"

    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['venue', 'start_time', 'end_time']),
        ]
