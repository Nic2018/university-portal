from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import datetime, date, timedelta
from django.utils.safestring import mark_safe

# Import your specific models, forms, and the utils helper
from .models import Venue, Booking
from .forms import BookingForm, VenueSearchForm
from .utils import Calendar

# ==========================================
# AUTHENTICATION VIEWS
# ==========================================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'index.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return render(request, 'register.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        
        if first_name and last_name:
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        messages.success(request, "Account created successfully! Please login.")
        return redirect('login')

    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('login')


# ==========================================
# MAIN APP VIEWS
# ==========================================

@login_required(login_url='login')
def dashboard_view(request):
    return render(request, 'dashboard.html')

@login_required(login_url='login')
def venue_list_view(request):
    form = VenueSearchForm(request.GET)
    venues = Venue.objects.all()

    if form.is_valid():
        query = form.cleaned_data.get('query')
        if query:
            venues = venues.filter(
                Q(name__icontains=query) | 
                Q(location__icontains=query)
            )

    return render(request, 'venue_list.html', {'venues': venues, 'form': form})

@login_required(login_url='login')
def create_booking_view(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user 
            booking.save()
            messages.success(request, "Booking request submitted successfully!")
            return redirect('dashboard')
    else:
        form = BookingForm()
    
    return render(request, 'create_booking.html', {'form': form})

# --- CALENDAR VIEW ---
@login_required(login_url='login')
def calendar_view(request):
    # 1. Get the current year/month from URL or default to today
    d = get_date(request.GET.get('month', None))
    
    # 2. Instantiate our custom Calendar class
    cal = Calendar(d.year, d.month)
    
    # 3. Create the HTML for the calendar
    html_cal = cal.formatmonth(withyear=True)
    
    # 4. Calculate Prev/Next month for navigation buttons
    prev_month = d.replace(day=1) - timedelta(days=1)
    next_month = d.replace(day=28) + timedelta(days=4)
    
    context = {
        'calendar': mark_safe(html_cal),
        'prev_month': f"month={prev_month.year}-{prev_month.month}",
        'next_month': f"month={next_month.year}-{next_month.month}",
    }

    return render(request, 'calendar.html', context)

# Helper for the calendar
def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()


# ==========================================
# USER FEATURES (My Bookings & Profile)
# ==========================================

@login_required(login_url='login')
def my_bookings_view(request):
    # Fetch user's bookings, newest first
    bookings = Booking.objects.filter(user=request.user).order_by('-start_time')
    return render(request, 'my_bookings.html', {'bookings': bookings})

@login_required(login_url='login')
def delete_booking_view(request, booking_id):
    # Only allow deleting if the booking belongs to the logged-in user
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if request.method == 'POST':
        booking.delete()
        messages.success(request, "Booking cancelled successfully.")
        
    return redirect('my_bookings')

@login_required(login_url='login')
def profile_view(request):
    user = request.user
    
    if request.method == 'POST':
        # 1. Handle "Update Details" Form
        if 'update_profile' in request.POST:
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.save()
            messages.success(request, "Profile details updated successfully!")
            return redirect('profile')

        # 2. Handle "Change Password" Form
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
                # This keeps the user logged in after changing password
                update_session_auth_hash(request, user) 
                messages.success(request, "Password changed successfully!")
                return redirect('profile')

    return render(request, 'profile.html')