from django.contrib import admin
from django.utils.html import format_html
from django.core.mail import send_mail  # <--- NEW IMPORT
from django.conf import settings        # <--- NEW IMPORT
from .models import Venue, Booking

# Manage Venues
@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity', 'equipment') 
    search_fields = ('name', 'location') 

# Manage Bookings
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'user', 'venue', 'start_time', 'colored_status', 'purpose', 'document')
    list_filter = ('status', 'venue', 'start_time', 'purpose')
    search_fields = ('event_name', 'user__username', 'description')
    readonly_fields = ('created_at',)

    # Use Search Boxes & Radio Buttons
    autocomplete_fields = ['venue', 'user']
    radio_fields = {
        'purpose': admin.HORIZONTAL,
        'status': admin.HORIZONTAL
    }

    actions = ['approve_bookings', 'reject_bookings']

    # Color-Coded Status Label
    @admin.display(description='Status')
    def colored_status(self, obj):
        if obj.status == 'APPROVED':
            color = 'green'
            icon = '✅'
        elif obj.status == 'REJECTED':
            color = 'red'
            icon = '❌'
        else:
            color = 'orange'
            icon = '⏳'
            
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color, icon, obj.get_status_display()
        )

    # --- UPDATED ACTION: APPROVE & SEND EMAIL ---
    @admin.action(description='Mark selected bookings as APPROVED')
    def approve_bookings(self, request, queryset):
        # 1. Update status in Database
        updated_count = queryset.update(status='APPROVED')
        
        # 2. Loop through and send emails
        for booking in queryset:
            if booking.user.email: # Check if user has an email
                subject = f"Booking Approved: {booking.event_name} ✅"
                message = f"""
                Hi {booking.user.first_name},

                Good news! Your booking request has been APPROVED by the admin.

                Event: {booking.event_name}
                Venue: {booking.venue.name}
                Time: {booking.start_time.strftime('%Y-%m-%d %H:%M')}
                
                Please arrive on time.
                """
                
                try:
                    send_mail(
                        subject,
                        message,
                        'admin@university.com', # From Email
                        [booking.user.email],   # To Email
                        fail_silently=True,
                    )
                except Exception as e:
                    print(f"Error sending email: {e}")

        self.message_user(request, f"{updated_count} bookings marked as APPROVED & notification emails sent.")

    @admin.action(description='Mark selected bookings as REJECTED')
    def reject_bookings(self, request, queryset):
        updated_count = queryset.update(status='REJECTED')
        self.message_user(request, f"{updated_count} bookings were marked as REJECTED.")