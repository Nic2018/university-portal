from django.contrib import admin
from django.urls import path, include
from django.conf import settings             # <--- Import this
from django.conf.urls.static import static   # <--- Import this

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
]

# Add this snippet to serve media files in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)