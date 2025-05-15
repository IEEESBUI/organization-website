# Tambahkan di urls.py utama
from django.urls import path
from articleDetails.views import ArticleDetailView
from . import views
urlpatterns = [
    path('/<slug:slug>/', ArticleDetailView.as_view(), name='article_detail'),
    # path('', views.show_article_details, name='show_article_details'),
]