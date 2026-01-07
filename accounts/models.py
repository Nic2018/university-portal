from django.db import models
from django.contrib.auth.models import User

# 1. The Venue Table (Stores info about Classrooms, Labs, Halls)
class Venue(models.Model):
    name = models.CharField(max_length=200, help_text="e.g. Lecture Hall A")
    location = models.CharField(max_length=200, help_text="e.g. Block B, Level 2")
    capacity = models.IntegerField(help_text="How many people can fit?")
    has_projector = models.BooleanField(default=False)
    has_ac = models.BooleanField(default=True, verbose_name="Has A/C")
    
    # This just makes it look nice in the Admin panel
    def __str__(self):
        return f"{self.name} ({self.location})"

# 2. The Booking Table (Links a Student to a Venue for a specific time)
class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    # Relationships (The lines in your diagram)
    user = models.ForeignKey(User, on_delete=models.CASCADE) # If student is deleted, delete their bookings
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE) # If room is deleted, delete bookings for it
    
    # Event Details
    event_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Timing
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    # Admin Approval Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True) # Automatically set when created

    def __str__(self):
        return f"{self.event_name} by {self.user.username}"
