# Tambahkan di urls.py utama
from django.urls import path
from . import views

urlpatterns = [
    path('', views.show_article_details, name='show_article_details'),
]