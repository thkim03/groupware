from django.urls import path
from . import views

app_name = 'purchase'

urlpatterns = [
    path('create/', views.purchase_create, name='purchase_create'),
    path('<int:pk>/', views.purchase_detail, name='purchase_detail'),
    path('list/', views.purchase_list, name='purchase_list'),
]
