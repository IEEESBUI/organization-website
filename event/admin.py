from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'location', 'is_upcoming')
    list_filter = ('date',)
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'date'
    readonly_fields = ('is_upcoming',)
    
    def is_upcoming(self, obj):
        return obj.is_upcoming
    is_upcoming.boolean = True
    is_upcoming.short_description = 'Upcoming'