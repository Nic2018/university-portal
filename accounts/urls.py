from django.urls import path
from . import views

urlpatterns = [
    # --- Authentication URLs ---
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # --- Dashboard URL ---
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # --- Feature URLs ---
    path('venues/', views.venue_list_view, name='venue_list'),
    path('book/', views.create_booking_view, name='create_booking'),
    path('calendar/', views.calendar_view, name='calendar'),

    # --- NEW: My Bookings & Cancellation ---
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    
    # This URL needs <int:booking_id> so we know WHICH booking to delete
    path('delete-booking/<int:booking_id>/', views.delete_booking_view, name='delete_booking'),
    
    path('profile/', views.profile_view, name='profile'),
]