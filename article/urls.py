# Tambahkan di urls.py utama
from django.urls import path
from . import views
from article.views import ArticleListView, ArticleDetailView
urlpatterns = [
    # path('', views.show_article, name='show_article'),
    # path('/<slug:slug>/', ArticleDetailView.as_view(), name='article_detail'),
    path('', ArticleListView.as_view(), name='articles'),
]