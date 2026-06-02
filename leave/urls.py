from django.urls import path
from . import views

app_name = 'leave'

urlpatterns = [
    path('create/', views.leave_create, name='leave_create'),
    path('<int:pk>/', views.leave_detail, name='leave_detail'),
    path('list/', views.leave_list, name='leave_list'),
]
