from django.db import models
from django.contrib.auth.models import User

# 1. The Venue Table
class Venue(models.Model):
    name = models.CharField(max_length=200, help_text="e.g. Lecture Hall A")
    location = models.CharField(max_length=200, help_text="e.g. Block B, Level 2")
    capacity = models.IntegerField(help_text="How many people can fit?")
    equipment = models.CharField(max_length=200, blank=True, help_text="e.g. Projector, Wifi, AC")
    
    def __str__(self):
        return f"{self.name} ({self.location})"

# 2. The Booking Table
class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    # NEW: Purpose Choices for the dropdown
    PURPOSE_CHOICES = [
        ('STUDY', 'Study'),
        ('EVENT', 'Event'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    
    # NEW: Purpose Field (Defaults to Study)
    purpose = models.CharField(max_length=10, choices=PURPOSE_CHOICES, default='STUDY')

    # UPDATED: event_name is now optional (blank=True) because "Study" sessions might auto-fill it
    event_name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    
    # NEW: Document Upload (Optional)
    # This stores files in a folder named 'booking_docs' inside your media directory
    document = models.FileField(upload_to='booking_docs/', blank=True, null=True)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    # Stores the status (Default is 'PENDING')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # NEW: Additional Equipment Requests
    addon_equipment = models.TextField(blank=True, null=True, help_text="List any extra equipment needed (e.g., Extra Mic, Extension Cord).")

    def __str__(self):
        return f"{self.event_name} - {self.status}"