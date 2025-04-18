from django.contrib import admin
from .models import Division, Activity, Project, Leader

class ActivityInline(admin.TabularInline):
    model = Activity
    extra = 1

class DivisionAdmin(admin.ModelAdmin):
    list_display = ('name', 'id_name', 'color')
    search_fields = ('name', 'description')
    inlines = [ActivityInline]

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'division')
    list_filter = ('division',)
    search_fields = ('title', 'description')

class LeaderAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'division')
    list_filter = ('division',)
    search_fields = ('name', 'position')

admin.site.register(Division, DivisionAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Leader, LeaderAdmin) 