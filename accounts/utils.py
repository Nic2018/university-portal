from calendar import HTMLCalendar
from .models import Booking

class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super(Calendar, self).__init__()

    def formatday(self, day, bookings):
        # 1. Get events for this day
        events_per_day = bookings.filter(
            start_time__year=day.year,
            start_time__month=day.month,
            start_time__day=day.day
        )
        
        d = ''
        for event in events_per_day:
            d += f'''
            <div class="event-box"> 
                <span class="event-time">{event.start_time.strftime("%I:%M%p").lstrip("0").lower()}</span>
                <span class="event-title">{event.event_name}</span>
            </div>
            '''

        # 2. Prepare the date string for the URL (e.g., "2026-01-15")
        date_str = day.strftime('%Y-%m-%d')
        
        # 3. Create the Clickable Attributes
        # We add 'onclick' to send the user to the booking page with the date
        click_action = f"onclick=\"window.location.href='/book/?date={date_str}'\""
        style = "style='cursor: pointer; position: relative;'"

        # 4. Render the Cell
        # If it's a day from another month, we add the 'other-month' class but keep it clickable
        if day.month != self.month:
            return f"<td class='other-month' {click_action} {style}><span class='date'>{day.day}</span><ul> {d} </ul></td>"
        
        # Standard day
        return f"<td {click_action} {style}><span class='date'>{day.day}</span><ul> {d} </ul></td>"

    def formatweek(self, theweek, bookings):
        week = ''
        for day in theweek:
            week += self.formatday(day, bookings)
        return f'<tr> {week} </tr>'

    def formatmonth(self, withyear=True):
        bookings = Booking.objects.all()

        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdatescalendar(self.year, self.month):
            cal += self.formatweek(week, bookings)
        cal += '</table>'
        return cal