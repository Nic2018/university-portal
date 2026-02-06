from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Venue, Booking, VenueSchedule

# ==========================================
# MANAGE SCHEDULE
# ==========================================
@admin.register(VenueSchedule)
class VenueScheduleAdmin(admin.ModelAdmin):
    list_display = ('schedule_display', 'open_hour', 'close_hour', 'slot_duration_minutes', 'days_in_advance')
    fieldsets = (
        ('Operating Hours', {
            'fields': ('open_hour', 'close_hour'),
            'description': 'Set the global operating hours for all venues (24-hour format, e.g., 8 to 20 for 8 AM to 8 PM)'
        }),
        ('Time Slot Configuration', {
            'fields': ('slot_duration_minutes', 'days_in_advance'),
            'description': 'Configure duration of each slot and how far in advance users can book'
        }),
    )

    @admin.display(description='Schedule')
    def schedule_display(self, obj):
        return f"{obj.open_hour:02d}:00 - {obj.close_hour:02d}:00"

    def has_add_permission(self, request):
        # Only allow one schedule entry
        return not VenueSchedule.objects.exists()

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
    list_display = ('event_name', 'user', 'venue', 'start_time', 'colored_status', 'purpose', 'time_slot_display', 'approved_by_display')
    list_filter = ('status', 'venue', 'start_time', 'purpose', 'created_at')
    search_fields = ('event_name', 'user__username', 'description')
    readonly_fields = ('created_at', 'updated_at', 'qr_code_display')

    fieldsets = (
        ('Booking Details', {
            'fields': ('user', 'venue', 'event_name', 'description', 'purpose')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time', 'time_slot')
        }),
        ('Equipment & Documents', {
            'fields': ('addon_equipment', 'document')
        }),
        ('Status & Approval', {
            'fields': ('status', 'approved_by', 'approved_at')
        }),
        ('QR Code', {
            'fields': ('qr_code_display',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['approve_bookings', 'reject_bookings']

    # Display QR Code
    @admin.display(description='QR Code')
    def qr_code_display(self, obj):
        if obj.qr_code:
            return mark_safe(f'<img src="{obj.qr_code.url}" width="200" height="200">')
        return "No QR code generated"

    # Display time slot if selected
    @admin.display(description='Time Slot')
    def time_slot_display(self, obj):
        if obj.time_slot:
            return f"🎯 {obj.time_slot}"
        return "—"

    # Display approved by info
    @admin.display(description='Approved By')
    def approved_by_display(self, obj):
        if obj.approved_by:
            return f"{obj.approved_by.username} ({obj.approved_at.strftime('%Y-%m-%d %H:%M')})"
        return "—"

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

    # --- ACTION 1: APPROVE & SEND EMAIL & TRACK APPROVAL ---
    @admin.action(description='✅ Approve selected bookings')
    def approve_bookings(self, request, queryset):
        for booking in queryset:
            booking.status = 'APPROVED'
            booking.approved_by = request.user
            booking.approved_at = timezone.now()
            booking.save()

            # Send email notification
            if booking.user.email:
                subject = f"Booking Approved: {booking.event_name} ✅"
                message = f"""
Hi {booking.user.first_name or booking.user.username},

Great news! Your booking request has been APPROVED.

📍 Event: {booking.event_name}
📌 Venue: {booking.venue.name} ({booking.venue.location})
⏰ Time: {booking.start_time.strftime('%Y-%m-%d %H:%M')} to {booking.end_time.strftime('%H:%M')}
🎯 Purpose: {booking.get_purpose_display()}

Please arrive on time. Your QR entry pass is ready!

Best regards,
Campus Booking Admin
                """
                try:
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [booking.user.email], fail_silently=True)
                except Exception as e:
                    print(f"Error sending email: {e}")

        self.message_user(request, f"✅ {queryset.count()} bookings approved & user notifications sent.")

    # --- ACTION 2: REJECT & SEND EMAIL ---
    @admin.action(description='❌ Reject selected bookings')
    def reject_bookings(self, request, queryset):
        for booking in queryset:
            booking.status = 'REJECTED'
            booking.approved_by = request.user
            booking.approved_at = timezone.now()
            booking.save()

            # Send email notification
            if booking.user.email:
                subject = f"Booking Update: {booking.event_name} ❌"
                message = f"""
Hi {booking.user.first_name or booking.user.username},

We regret to inform you that your booking request has been REJECTED.

📍 Event: {booking.event_name}
📌 Venue: {booking.venue.name} ({booking.venue.location})
⏰ Requested Time: {booking.start_time.strftime('%Y-%m-%d %H:%M')} to {booking.end_time.strftime('%H:%M')}

Possible reasons:
- Venue not available at that time
- Insufficient capacity
- Policy violation

Please try booking a different time slot or contact support for more details.

Best regards,
Campus Booking Admin
                """
                try:
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [booking.user.email], fail_silently=True)
                except Exception as e:
                    print(f"Error sending email: {e}")

        self.message_user(request, f"❌ {queryset.count()} bookings rejected & user notifications sent.")