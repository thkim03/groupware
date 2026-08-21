from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('check-in/', views.check_in, name='check_in'),
    path('check-out/', views.check_out, name='check_out'),
    path('my/', views.my_attendance, name='my_attendance'),
    path('my/<int:year>/<int:month>/', views.my_attendance, name='my_attendance_month'),
    path('edit/<int:pk>/', views.edit_attendance, name='edit_attendance'),
    path('admin/', views.admin_attendance, name='admin_attendance'),
    path('admin/<int:year>/<int:month>/', views.admin_attendance, name='admin_attendance_month'),
    path('admin/edit/<int:pk>/', views.admin_edit_attendance, name='admin_edit_attendance'),
    path('admin/excel/<int:year>/<int:month>/', views.admin_attendance_excel, name='admin_attendance_excel'),
    path('direct-add/', views.direct_add, name='direct_add'),
]
