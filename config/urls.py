from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('accounts/', include('accounts.urls')),
    path('attendance/', include('attendance.urls')),
    path('approvals/', include('approvals.urls')),
    path('leave/', include('leave.urls')),
    path('trip/', include('trip.urls')),
    path('purchase/', include('purchase.urls')),
    path('expense/', include('expense.urls')),
    path('schedule/', include('schedule.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
