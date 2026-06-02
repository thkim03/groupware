from django.urls import path
from . import views

app_name = 'expense'

urlpatterns = [
    path('create/', views.expense_create, name='expense_create'),
    path('<int:pk>/', views.expense_detail, name='expense_detail'),
    path('list/', views.expense_list, name='expense_list'),
]
