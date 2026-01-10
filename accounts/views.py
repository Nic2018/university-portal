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
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
import re  # Importing regex for smarter matching

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
        # Handles request.FILES for document uploads
        form = BookingForm(request.POST, request.FILES)
        
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user 
            
            # --- AUTO-FILL LOGIC ---
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
                messages.error(request, "⚠️ Booking Failed! That time slot is already taken.")
            else:
                booking.status = 'PENDING'
                booking.save()
                messages.success(request, "Booking request submitted successfully!")
            
            return redirect('dashboard')
    else:
        # --- GET REQUEST (Page Load) ---
        initial_data = {}
        
        # Check if a Venue ID was passed
        venue_id = request.GET.get('venue')
        if venue_id:
            initial_data['venue'] = venue_id
            
        # Check if a Date was passed
        date_param = request.GET.get('date') 
        if date_param:
            initial_data['start_time'] = f"{date_param} 09:00"
            initial_data['end_time'] = f"{date_param} 22:00"

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

# ==========================================
# 🤖 CAMPUS-BOT AI LOGIC
# ==========================================

@csrf_exempt
def ai_chat_response(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').lower()
            
            print(f"User Message: {user_message}") 

            # ---------------------------------------------------------
            # 1. GREETINGS
            # ---------------------------------------------------------
            if any(word in user_message for word in ['hello', 'hi', 'hey', 'greetings']):
                return JsonResponse({'response': "Hello! 👋 I am CampusBot. Type a venue name (e.g., 'CQAR0001') to check its status."})

            # ---------------------------------------------------------
            # 2. RECOMMENDATION (By Capacity)
            # ---------------------------------------------------------
            if any(word in user_message for word in ['people', 'capacity', 'pax', 'fit']):
                import re
                numbers = re.findall(r'\d+', user_message)
                if numbers:
                    required_pax = int(numbers[0])
                    options = Venue.objects.filter(capacity__gte=required_pax).order_by('capacity')
                    
                    if options.exists():
                        names = ", ".join([f"{v.name} ({v.capacity})" for v in options[:2]])
                        return JsonResponse({'response': f"💡 I recommend: {names}."})
                    else:
                        return JsonResponse({'response': f"⚠️ No single room can fit {required_pax} people."})
                else:
                    return JsonResponse({'response': "How many people? (e.g., 'Room for 30 people')"})

            # ---------------------------------------------------------
            # 3. DIRECT VENUE CHECK (The Fix!)
            # ---------------------------------------------------------
            # We look for a venue name match FIRST, before checking for "availability" keywords.
            venues = Venue.objects.all()
            found_venue = None
            
            for v in venues:
                # Check if the exact venue name (or a significant part) is in the message
                # e.g., if user types "CQAR0001", this will match.
                if v.name.lower() in user_message:
                    found_venue = v
                    break
            
            if found_venue:
                now = timezone.now()
                is_booked = Booking.objects.filter(
                    venue=found_venue, 
                    start_time__lte=now, 
                    end_time__gte=now,
                    status='APPROVED'
                ).exists()
                
                if is_booked:
                    return JsonResponse({'response': f"🚫 {found_venue.name} is currently BOOKED."})
                else:
                    return JsonResponse({'response': f"✅ {found_venue.name} is AVAILABLE right now!"})

            # ---------------------------------------------------------
            # 4. KEYWORD FALLBACK
            # ---------------------------------------------------------
            # If user asked "is it free?" but we couldn't find a venue name above
            if any(word in user_message for word in ['available', 'free', 'open', 'status', 'booked', 'check']):
                names = ", ".join([v.name for v in venues[:3]])
                return JsonResponse({'response': f"Which venue? Try naming one specifically, like: {names}..."})

            # ---------------------------------------------------------
            # 5. FINAL FALLBACK
            # ---------------------------------------------------------
            return JsonResponse({'response': "I didn't catch that. Try typing a venue name like 'CQAR0001' directly."})

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'response': "⚠️ My brain hit a snag. Please try again."})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required(login_url='login')
def dashboard_view(request):
    # 1. Get counts for the chart
    pending_count = Booking.objects.filter(user=request.user, status='PENDING').count()
    approved_count = Booking.objects.filter(user=request.user, status='APPROVED').count()
    rejected_count = Booking.objects.filter(user=request.user, status='REJECTED').count()
    
    # 2. Pass data to template
    context = {
        'p_count': pending_count,
        'a_count': approved_count,
        'r_count': rejected_count
    }
    return render(request, 'dashboard.html', context)