# Animated Notifications System

## How to Use

This notification system automatically:
- ✅ Slides in from left smoothly
- ✅ Auto-dismisses after 4 seconds
- ✅ Slides out to the right when dismissing
- ✅ Can be clicked to dismiss immediately
- ✅ Supports success, error, warning, and info messages

## Usage in Templates

Simply add this one line to any Django template where you want notifications to appear:

```django
{% include "notifications.html" %}
```

## Features

### Automatic Styling for Message Tags:
- `success` - Green background with checkmark
- `error` - Red background with X mark
- `warning` - Orange background with warning icon
- `info` - Blue background with info icon

### How It Works:

1. **Django messages are sent from views:**
   ```python
   messages.success(request, "Booking updated successfully! Admin approval pending.")
   messages.error(request, "❌ Validation Error: Time slot conflicts...")
   ```

2. **Notifications.html template displays them with animations**

3. **JavaScript handles:**
   - 4-second auto-dismiss timer
   - Click-to-dismiss functionality
   - Smooth CSS animations

## Animation Details

### Slide In (0.5s):
```
Starts: opacity 0%, translateX(-100%)
Ends: opacity 100%, translateX(0)
```

### Slide Out (0.5s):
```
Starts: opacity 100%, translateX(0)
Ends: opacity 0%, translateX(100%)
```

## Files Using This System

- ✅ `templates/notifications.html` - The reusable component
- ✅ `templates/my_bookings.html` - Uses {% include %}
- ✅ `templates/modify_booking.html` - Uses {% include %}

## To Add to Other Templates

Find the `{% if messages %}` section and replace with:
```django
{% include "notifications.html" %}
```

Or simply add it above your main content section.

## Customization

To change the auto-dismiss time (currently 4000ms):
- Edit `notifications.html`, line with `setTimeout(() => {`
- Change `4000` to your desired milliseconds

Example: `2000` = 2 seconds, `6000` = 6 seconds

## Styling Customization

The notification colors are defined in `notifications.html`:
- `.alert-success` - Success messages
- `.alert-error` - Error messages  
- `.alert-warning` - Warning messages
- `.alert-info` - Info messages

Modify the `background` and `color` properties to customize.
