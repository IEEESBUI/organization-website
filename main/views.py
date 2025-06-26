# Tambahkan di views.py di aplikasi utama
from django.shortcuts import render
from event.models import Event
from article.models import Article
from django.utils import timezone

def homepage(request):
    today = timezone.now().date()
    events = Event.objects.filter(date__gte=today).order_by('date', 'time')[:3]
    articles = Article.objects.filter(status='published').order_by('-created_at')[:3]
    return render(request, 'homepage.html', {
        'events': events,
        'articles': articles,
    })