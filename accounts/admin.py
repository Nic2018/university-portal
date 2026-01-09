from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Venue, Booking

# ==========================================
# MANAGE VENUES
# ==========================================
@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity', 'equipment', 'venue_status') 
    search_fields = ('name', 'location') 

    # --- REAL-TIME AVAILABILITY CHECK ---
    @admin.display(description='Current Status')
    def venue_status(self, obj):
        try:
            now = timezone.now()
            
            # Check for bookings happening RIGHT NOW
            is_busy = Booking.objects.filter(
                venue=obj,
                status='APPROVED',
                start_time__lte=now,
                end_time__gte=now
            ).exists()

            if is_busy:
                return mark_safe('<span style="color: red; font-weight: bold;">🔴 Booked</span>')
            else:
                return mark_safe('<span style="color: green; font-weight: bold;">🟢 Available</span>')
        except Exception:
            return mark_safe('<span style="color: gray;">⚠️ Error</span>')

# ==========================================
# MANAGE BOOKINGS
# ==========================================
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

    # --- ACTION 1: APPROVE & SEND EMAIL ---
    @admin.action(description='Mark selected bookings as APPROVED')
    def approve_bookings(self, request, queryset):
        updated_count = queryset.update(status='APPROVED')
        
        for booking in queryset:
            if booking.user.email:
                subject = f"Booking Approved: {booking.event_name} ✅"
                message = f"""
                Hi {booking.user.first_name},

                Good news! Your booking request has been APPROVED.

                Event: {booking.event_name}
                Venue: {booking.venue.name}
                Time: {booking.start_time.strftime('%Y-%m-%d %H:%M')}
                
                Please arrive on time.
                """
                try:
                    send_mail(subject, message, 'admin@university.com', [booking.user.email], fail_silently=True)
                except:
                    pass

        self.message_user(request, f"{updated_count} bookings marked as APPROVED & emails sent.")

    # --- ACTION 2: REJECT & SEND EMAIL (UPDATED) ---
    @admin.action(description='Mark selected bookings as REJECTED')
    def reject_bookings(self, request, queryset):
        updated_count = queryset.update(status='REJECTED')
        
        # Now we loop through rejected bookings to send the notification
        for booking in queryset:
            if booking.user.email:
                subject = f"Booking Update: {booking.event_name} ❌"
                message = f"""
                Hi {booking.user.first_name},

                We regret to inform you that your booking request has been REJECTED.

                Event: {booking.event_name}
                Venue: {booking.venue.name}
                Time: {booking.start_time.strftime('%Y-%m-%d %H:%M')}
                
                Please contact the admin for more details or try booking a different slot.
                """
                try:
                    send_mail(subject, message, 'admin@university.com', [booking.user.email], fail_silently=True)
                except:
                    pass

        self.message_user(request, f"{updated_count} bookings marked as REJECTED & emails sent.")