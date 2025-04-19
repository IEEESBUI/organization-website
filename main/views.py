# Tambahkan di views.py di aplikasi utama
from django.shortcuts import render

def homepage(request):
    return render(request, 'homepage.html')