from django.urls import path
from . import views

app_name = 'divisions'

urlpatterns = [
    path('', views.divisions_page, name='divisions_page'),
] 