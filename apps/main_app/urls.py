from django.urls import path
from . import views

urlpatterns = [
    # Asosiy sahifa
    path('', views.home, name='home'),

    # Tashxis qo'yish
    path('diagnose/', views.diagnose_thyroid, name='diagnose'),

    # Tashxis detali (UUID bilan)
    path('diagnosis/<uuid:uuid>/', views.diagnosis_detail, name='diagnosis_detail'),

    # Yuklab olish
    path('diagnosis/<uuid:uuid>/download/', views.download_diagnosis, name='download_diagnosis'),

    # Ro'yxat (Admin uchun)
    path('diagnoses/', views.diagnosis_list, name='diagnosis_list'),
]