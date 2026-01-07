# 🎓 University Resource & Booking Portal

A premium, web-based student portal built with **Django**. This system allows university students to view class schedules, search for venues, and book facilities (labs, halls, classrooms) with a modern, glassmorphic user interface.

## ✨ Key Features

### 👤 User Experience (Premium UI)
- **Modern Dashboard:** Glassmorphic design, sidebar navigation with custom tooltips, and responsive cards.
- **Secure Authentication:** Split-screen Login & Register pages with gradient backgrounds.
- **Profile Management:** dedicated page to update personal details and change passwords securely.

### 📅 Smart Calendar & Scheduling
- **Interactive Calendar:** Custom-built Python HTML calendar.
- **Click-to-Book:** Clicking any date on the calendar instantly redirects to the booking form with that date pre-selected.
- **Month Navigation:** Seamlessly scroll between previous and upcoming months.

### 📝 Booking System
- **Smart Form:** Auto-fills **Start Time (09:00)** and **End Time (22:00)** for convenience.
- **Visual Date Picker:** Integrated **Flatpickr.js** for a professional date/time selection popup.
- **Conflict Prevention:** Logic to prevent double-booking (via UI constraints).
- **My Bookings:** A dedicated list view where users can track and **cancel** their reservations.

### 📍 Venue Discovery
- **Searchable List:** Filter venues by name or location.
- **Amenity Badges:** Visual indicators for Projectors, A/C, or Fans.
- **Capacity Indicators:** See room sizes at a glance.

---

## 🛠️ Technology Stack

- **Backend:** Python 3, Django Framework
- **Database:** SQLite (Default) / Compatible with MySQL
- **Frontend:** HTML5, CSS3 (Glassmorphism), JavaScript
- **Libraries:**
  - **Flatpickr:** For time/date selection.
  - **FontAwesome:** For premium icons.
  - **Poppins Font:** For modern typography.

---

## 📂 Project Structure

```text
cse/
├── manage.py                   # Django task runner
├── cse/                        # Project settings
├── accounts/                   # Main application
│   ├── models.py               # Database tables (Venue, Booking)
│   ├── views.py                # Logic for Dashboard, Profile, Calendar
│   ├── utils.py                # Custom Calendar Generation Logic
│   └── forms.py                # Booking & Search Forms
├── templates/                  # Frontend HTML files
│   ├── index.html              # Login Page
│   ├── register.html           # Registration Page
│   ├── dashboard.html          # Main User Dashboard
│   ├── calendar.html           # Schedule View
│   ├── create_booking.html     # Booking Form
│   ├── venue_list.html         # Venue Search
│   ├── my_bookings.html        # Booking History & Cancellation
│   └── profile.html            # User Settings
├── requirements.txt            # Python dependencies
└── db.sqlite3                  # Database file