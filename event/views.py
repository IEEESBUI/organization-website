from django.shortcuts import render

def show_event(request):
    return render(request, 'event.html')