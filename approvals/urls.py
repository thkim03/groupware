from django.urls import path
from . import views

app_name = 'approvals'

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('sent/', views.sent_box, name='sent'),
    path('approve/<int:doc_pk>/', views.approve_action, name='approve_action'),
    path('cancel/<int:doc_pk>/', views.cancel_doc, name='cancel_doc'),
]
