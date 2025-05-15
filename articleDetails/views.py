from django.shortcuts import render
from django.views.generic import ListView, DetailView
from article.models import Article, Category
from django.template.defaulttags import register

# def show_article_details(request):
    # return render(request, 'articleDetails.html')

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'articleDetails.html'
    context_object_name = 'article'
    slug_url_kwarg = 'slug'
    
    def get_object(self):
        obj = super().get_object()
        # Increment view count
        obj.view_count += 1
        obj.save()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add related articles
        article = self.get_object()
        related_articles = Article.objects.filter(
            categories__in=article.categories.all(),
            status='published'
        ).exclude(id=article.id).distinct()[:3]
        context['related_articles'] = related_articles
        return context

# Custom template filter for URL parameters
@register.simple_tag
def url_replace(request, field, value):
    """
    Custom template filter to replace URL parameters
    Args:
        request: HTTP request object
        field (str): Parameter name to replace
        value (str): New value for the parameter
    """
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()
