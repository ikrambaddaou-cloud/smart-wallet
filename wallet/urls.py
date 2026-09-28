from django.urls import path
from . import views # This is correct here because views.py is in the same folder

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]
from django.urls import path
from . import views

urlpatterns = [
    # Changez 'views.wallet_dashboard' par 'views.dashboard'
    path('', views.dashboard, name='dashboard'), 
]