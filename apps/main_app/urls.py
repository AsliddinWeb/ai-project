from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('diagnose/', views.diagnose_thyroid, name='diagnose'),
]