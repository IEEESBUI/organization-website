from django.shortcuts import render

def show_article_details(request):
    return render(request, 'articleDetails.html')