# Tambahkan di urls.py utama
from django.urls import path
from . import views

urlpatterns = [
    path('', views.show_about, name='show_about'),
]