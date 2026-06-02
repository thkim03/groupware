from django.urls import path
from . import views

app_name = 'trip'

urlpatterns = [
    path('create/', views.trip_create, name='trip_create'),
    path('<int:pk>/', views.trip_detail, name='trip_detail'),
    path('list/', views.trip_list, name='trip_list'),
]
