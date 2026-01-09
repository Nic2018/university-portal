import qrcode
from io import BytesIO
from django.core.files import File
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

    PURPOSE_CHOICES = [
        ('STUDY', 'Study'),
        ('EVENT', 'Event'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    
    purpose = models.CharField(max_length=10, choices=PURPOSE_CHOICES, default='STUDY')
    event_name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    
    document = models.FileField(upload_to='booking_docs/', blank=True, null=True)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    
    addon_equipment = models.TextField(blank=True, null=True, help_text="List any extra equipment needed (e.g., Extra Mic, Extension Cord).")

    # --- NEW: QR Code Field ---
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # 1. Check if the booking is APPROVED and doesn't have a QR code yet
        if self.status == 'APPROVED' and not self.qr_code:
            # 2. Create the data string for the QR code
            qr_data = f"ENTRY PASS\nID: {self.id}\nUser: {self.user.username}\nEvent: {self.event_name}\nVenue: {self.venue.name}\nTime: {self.start_time}"
            
            # 3. Generate the QR image
            qr_img = qrcode.make(qr_data)
            
            # 4. Save image to a memory buffer
            canvas = BytesIO()
            qr_img.save(canvas, format='PNG')
            
            # 5. Save the image file to the database field
            file_name = f"qr_booking_{self.id}.png"
            self.qr_code.save(file_name, File(canvas), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.event_name} - {self.status}"