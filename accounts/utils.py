from datetime import datetime, timedelta
from calendar import HTMLCalendar
from .models import Booking

class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super(Calendar, self).__init__()

    # 1. Format each day
    def formatday(self, day, weekday):
        # Filter events for this day (Approved/Pending only)
        bookings = Booking.objects.filter(
            start_time__year=self.year, 
            start_time__month=self.month, 
            start_time__day=day
        ).exclude(status='REJECTED')

        # --- NEW: GENERATE DATE STRING (YYYY-MM-DD) ---
        # We need this to pass to the URL so the form knows which date to pick
        current_date = f"{self.year}-{self.month:02d}-{day:02d}"
        create_url = f"/create_booking/?date={current_date}"

        d = ''
        for event in bookings:
            # Yellow clickable event box
            d += f'''
                <a href="/booking_detail/{event.id}/" style="text-decoration: none; display: block;">
                    <div class="calendar-event">
                        <span class="event-time">{event.start_time.strftime("%H:%M")}</span>
                        <span class="event-title">{event.event_name}</span>
                    </div>
                </a>
            '''

        if day != 0:
            # --- THE FIX IS HERE ---
            # We wrap the day number {day} in a link to create_url
            # We also add a small "+" icon to make it obvious
            day_html = f'''
                <div class="day-header">
                    <a href="{create_url}" class="date-btn" title="Add Booking">
                        {day} <i class="fas fa-plus-circle add-icon"></i>
                    </a>
                </div>
            '''
            return f"<td>{day_html}<div class='day-events'>{d}</div></td>"
        
        return '<td></td>'

    # 2. Format a week
    def formatweek(self, theweek):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, weekday)
        return f'<tr> {week} </tr>'

    # 3. Format the month
    def formatmonth(self, withyear=True):
        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'<tr class="week-headers"><th>Mon</th><th>Tue</th><th>Wed</th><th>Thu</th><th>Fri</th><th>Sat</th><th>Sun</th></tr>\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week)}\n'
        cal += '</table>'
        return cal