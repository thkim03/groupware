from django.urls import path
from . import views

app_name = 'schedule'

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('events/', views.events_json, name='events_json'),
    path('create/', views.schedule_create, name='create'),
    path('<int:pk>/edit/', views.schedule_edit, name='edit'),
    path('<int:pk>/delete/', views.schedule_delete, name='delete'),
]
