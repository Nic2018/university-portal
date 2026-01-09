from django.urls import path
from . import views  # <--- IMPORTANT: This imports your views.py

urlpatterns = [
    # --- Authentication ---
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('guest_login/', views.guest_login_view, name='guest_login'),

    # --- Dashboard & Features ---
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('venue_list/', views.venue_list_view, name='venue_list'),
    path('calendar/', views.calendar_view, name='calendar'),

    # --- Booking ---
    path('create_booking/', views.create_booking_view, name='create_booking'),
    path('modify_booking/<int:booking_id>/', views.modify_booking_view, name='modify_booking'),
    
    # NEW PATH: This handles the link from the Calendar
    path('booking_detail/<int:booking_id>/', views.booking_detail_view, name='booking_detail'),

    # --- User Pages ---
    path('my_bookings/', views.my_bookings_view, name='my_bookings'),
    path('delete_booking/<int:booking_id>/', views.delete_booking_view, name='delete_booking'),
    path('profile/', views.profile_view, name='profile'),
    path('check_availability/', views.check_availability, name='check_availability'),
]