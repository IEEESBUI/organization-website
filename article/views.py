from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Article, Category
from django.template.defaulttags import register

class ArticleListView(ListView):
    model = Article
    template_name = 'article.html'
    context_object_name = 'articles'
    paginate_by = 9  # Show 9 articles per page
    
    def get_queryset(self):
        queryset = Article.objects.filter(status='published').order_by('-created_at')
        
        # Apply search filter
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(content__icontains=search_query) |
                Q(excerpt__icontains=search_query)
            )
        
        # Apply category filter
        category_filter = self.request.GET.get('category', '')
        if category_filter:
            category_ids = category_filter.split(',')
            queryset = queryset.filter(categories__id__in=category_ids).distinct()
        
        # Apply sorting
        sort_by = self.request.GET.get('sort', '')
        if sort_by == 'recent':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort_by == 'popular':
            queryset = queryset.order_by('-view_count')
        elif sort_by == 'az':
            queryset = queryset.order_by('title')
        elif sort_by == 'za':
            queryset = queryset.order_by('-title')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add categories to context
        context['categories'] = Category.objects.all()
        
        # Add featured article
        featured_articles = Article.objects.filter(is_featured=True, status='published').order_by('-created_at')
        if featured_articles.exists():
            context['featured_article'] = featured_articles.first()
        
        # Get selected categories for highlighting in the UI
        selected_categories = self.request.GET.get('category', '').split(',') if self.request.GET.get('category') else []
        context['selected_categories'] = selected_categories
        
        # Get category objects for display in active filters
        if selected_categories and selected_categories[0]:  # Check if not empty string
            context['selected_category_objects'] = Category.objects.filter(id__in=selected_categories)
        else:
            context['selected_category_objects'] = []
        
        return context

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'article_detail.html'
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
    Template tag to replace or add a GET parameter in the current URL
    """
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()