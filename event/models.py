from django.db import models
from django.urls import reverse
from django.utils import timezone

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image_url = models.URLField(help_text="URL to the event image")
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date', 'time']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('event_detail', args=[str(self.id)])
    
    @property
    def is_upcoming(self):
        """Automatically determine if this is an upcoming event based on date"""
        return self.date >= timezone.now().date()