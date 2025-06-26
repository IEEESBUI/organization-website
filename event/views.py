from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.utils import timezone
from .models import Event

class EventListView(ListView):
    model = Event
    template_name = 'event_list.html'
    context_object_name = 'events'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        context['upcoming_events'] = Event.objects.filter(date__gte=today).order_by('date', 'time')
        context['past_events'] = Event.objects.filter(date__lt=today).order_by('-date', 'time')
        return context

class EventDetailView(DetailView):
    model = Event
    template_name = 'event_detail.html'
    context_object_name = 'event'