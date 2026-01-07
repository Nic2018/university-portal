from django.contrib import admin
from .models import Venue, Booking

# This allows you to manage Venues in the Admin Panel
@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity', 'has_projector')
    search_fields = ('name', 'location')

# This allows you to see/approve Bookings
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'user', 'venue', 'start_time', 'status')
    list_filter = ('status', 'venue', 'start_time')
    actions = ['approve_booking', 'reject_booking']

    # Quick buttons to approve/reject multiple bookings at once
    def approve_booking(self, request, queryset):
        queryset.update(status='APPROVED')
    
    def reject_booking(self, request, queryset):
        queryset.update(status='REJECTED')