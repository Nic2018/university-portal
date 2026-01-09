from django.contrib import admin
from django.utils.html import format_html
from .models import Venue, Booking

# Manage Venues
@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity', 'equipment') 
    # This search_fields is REQUIRED for the booking autocomplete to work
    search_fields = ('name', 'location') 

# Manage Bookings
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'user', 'venue', 'start_time', 'colored_status', 'purpose', 'document')
    list_filter = ('status', 'venue', 'start_time', 'purpose')
    search_fields = ('event_name', 'user__username', 'description')
    readonly_fields = ('created_at',)

    # --- FIX 1: Use Search Boxes instead of Dropdowns ---
    # This fixes the "User" and "Venue" display issues
    autocomplete_fields = ['venue', 'user']

    # --- FIX 2: Use Radio Buttons for Purpose ---
    # This changes the "Purpose" dropdown to visible buttons
    radio_fields = {'purpose': admin.HORIZONTAL}

    # Bulk Actions
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

    @admin.action(description='Mark selected bookings as APPROVED')
    def approve_bookings(self, request, queryset):
        updated_count = queryset.update(status='APPROVED')
        self.message_user(request, f"{updated_count} bookings were successfully marked as APPROVED.")

    @admin.action(description='Mark selected bookings as REJECTED')
    def reject_bookings(self, request, queryset):
        updated_count = queryset.update(status='REJECTED')
        self.message_user(request, f"{updated_count} bookings were marked as REJECTED.")