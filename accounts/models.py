import qrcode
from io import BytesIO
from django.core.files import File
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

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
        
        # Check for clashes
        clashing = Booking.objects.filter(
            venue=self.venue,
            status='APPROVED',
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
