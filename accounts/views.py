from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import datetime, date, timedelta
from django.utils.safestring import mark_safe
from django.http import JsonResponse

from .models import Venue, Booking
from .forms import BookingForm, VenueSearchForm
from .utils import Calendar

# ==========================================
# AUTHENTICATION
# ==========================================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password'))
            if user:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid credentials.")
        else:
            messages.error(request, "Invalid credentials.")
    return render(request, 'index.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        user = User.objects.create_user(
            username=request.POST['username'],
            email=request.POST['email'],
            password=request.POST['password'],
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name')
        )
        user.save()
        messages.success(request, "Account created! Please login.")
        return redirect('login')
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def guest_login_view(request):
    user, created = User.objects.get_or_create(username='guest')
    if created:
        user.first_name = "Guest"
        user.last_name = "User"
        user.set_unusable_password()
        user.save()
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return redirect('dashboard')

# ==========================================
# MAIN FEATURES
# ==========================================

@login_required(login_url='login')
def dashboard_view(request):
    return render(request, 'dashboard.html')

@login_required(login_url='login')
def venue_list_view(request):
    venues = Venue.objects.all()
    query = request.GET.get('query')
    if query:
        venues = venues.filter(name__icontains=query)
    location = request.GET.get('location')
    if location:
        venues = venues.filter(location__icontains=location)
    capacity_filter = request.GET.get('capacity')
    if capacity_filter == 'small':
        venues = venues.filter(capacity__lt=20)
    elif capacity_filter == 'medium':
        venues = venues.filter(capacity__gte=20, capacity__lte=50)
    elif capacity_filter == 'large':
        venues = venues.filter(capacity__gt=50)
    return render(request, 'venue_list.html', {'venues': venues})

@login_required(login_url='login')
def create_booking_view(request):
    if request.user.username == 'guest':
        messages.error(request, "Guests cannot make bookings. Please register an account.")
        return redirect('dashboard')

    if request.method == 'POST':
        # UPDATED: Included request.FILES to handle document uploads
        form = BookingForm(request.POST, request.FILES)
        
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user 
            
            # --- AUTO-FILL LOGIC ---
            # If purpose is 'STUDY', auto-set the name so user doesn't have to type it
            if booking.purpose == 'STUDY':
                booking.event_name = "Study Session"

            # --- CLASH DETECTION LOGIC ---
            clashing_bookings = Booking.objects.filter(
                venue=booking.venue,
                status='APPROVED',
                start_time__lt=booking.end_time,
                end_time__gt=booking.start_time
            )

            if clashing_bookings.exists():
                # CLASH FOUND! -> ERROR ONLY (DO NOT SAVE)
                messages.error(request, "⚠️ Booking Failed! That time slot is already taken.")
            else:
                # NO CLASH -> SUCCESS
                booking.status = 'PENDING'
                booking.save()
                messages.success(request, "Booking request submitted successfully!")
            
            return redirect('dashboard')
    else:
        initial_data = {}
        venue_id = request.GET.get('venue')
        if venue_id:
            initial_data['venue'] = venue_id
        form = BookingForm(initial=initial_data)
    
    return render(request, 'create_booking.html', {'form': form})

# --- DETAIL VIEW ---
@login_required(login_url='login')
def booking_detail_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'booking_detail.html', {'booking': booking})

@login_required(login_url='login')
def modify_booking_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == 'POST':
        # Also need request.FILES here in case they update the document
        form = BookingForm(request.POST, request.FILES, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, "Booking updated successfully!")
            return redirect('my_bookings')
    else:
        form = BookingForm(instance=booking)
    return render(request, 'modify_booking.html', {'form': form, 'booking': booking})

@login_required(login_url='login')
def calendar_view(request):
    d = get_date(request.GET.get('month', None))
    cal = Calendar(d.year, d.month)
    html_cal = cal.formatmonth(withyear=True)
    prev_month = d.replace(day=1) - timedelta(days=1)
    next_month = d.replace(day=28) + timedelta(days=4)
    return render(request, 'calendar.html', {
        'calendar': mark_safe(html_cal),
        'prev_month': f"month={prev_month.year}-{prev_month.month}",
        'next_month': f"month={next_month.year}-{next_month.month}",
    })

def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()

@login_required(login_url='login')
def my_bookings_view(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-start_time')
    return render(request, 'my_bookings.html', {'bookings': bookings})

@login_required(login_url='login')
def delete_booking_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == 'POST':
        booking.delete()
        messages.success(request, "Booking cancelled successfully.")
    return redirect('my_bookings')

@login_required(login_url='login')
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        if user.username == 'guest':
            messages.error(request, "Guest accounts cannot update profile settings.")
            return redirect('profile')
        if 'update_profile' in request.POST:
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.save()
            messages.success(request, "Profile details updated successfully!")
            return redirect('profile')
        elif 'change_password' in request.POST:
            pass1 = request.POST.get('new_password')
            pass2 = request.POST.get('confirm_password')
            if pass1 != pass2:
                messages.error(request, "Passwords do not match!")
            elif len(pass1) < 6:
                messages.error(request, "Password must be at least 6 characters.")
            else:
                user.set_password(pass1)
                user.save()
                update_session_auth_hash(request, user) 
                messages.success(request, "Password changed successfully!")
                return redirect('profile')
    return render(request, 'profile.html')

# --- AJAX Availability Check ---
def check_availability(request):
    venue_id = request.GET.get('venue_id')
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')

    if venue_id and start_time and end_time:
        is_taken = Booking.objects.filter(
            venue_id=venue_id,
            status='APPROVED',
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()
        
        if is_taken:
            return JsonResponse({'status': 'unavailable'})
        else:
            return JsonResponse({'status': 'available'})

    return JsonResponse({'status': 'error'})