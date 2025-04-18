from django.shortcuts import render

def show_about(request):
    
    return render(request, 'about.html')