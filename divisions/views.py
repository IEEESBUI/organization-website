from django.shortcuts import render
from .models import Division, Project, Leader

def divisions_page(request):
    """
    View for displaying the IEEE SBUI divisions page
    """
    context = {
        'divisions': Division.objects.all().prefetch_related('activities'),
        'projects': Project.objects.all().select_related('division'),
        'leaders': Leader.objects.all().select_related('division'),
    }
    
    return render(request, 'divisions.html', context) 