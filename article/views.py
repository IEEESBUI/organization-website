from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Article, Category
from django.template.defaulttags import register

class ArticleListView(ListView):
    """
    view untuk menampilkan daftar artikel
    Args:
        ListView: Kelas dasar untuk menampilkan daftar objek
    Attributes:
        model (Article): Model artikel yang digunakan
        template_name (str): Nama template untuk menampilkan daftar artikel
        context_object_name (str): Nama konteks untuk daftar artikel
        paginate_by (int): Jumlah artikel per halaman
    Methods:
        get_queryset(): Mengambil daftar artikel berdasarkan filter dan sorting
        get_context_data(): Menambahkan kategori dan artikel unggulan ke konteks
        render_to_response(): Menangani respons AJAX
    Notes:
        - Artikel yang ditampilkan adalah artikel dengan status 'published'.
        - Artikel diurutkan berdasarkan tanggal pembuatan terbaru.
        - Halaman artikel menggunakan pagination.
        - Artikel dapat difilter berdasarkan kategori dan pencarian.
        - Artikel dapat diurutkan berdasarkan tanggal terbaru, tanggal terlama, popularitas, atau abjad (A-Z atau Z-A).
        - Kategori yang ditampilkan diambil dari model Category.
        - Artikel unggulan diambil dari model Article dengan atribut is_featured=True.
        - Mendukung respons AJAX untuk pembaruan dinamis.
    """
    model = Article
    template_name = 'article.html'
    context_object_name = 'articles'
    paginate_by = 3  # Show 3 articles per page
    
    def get_paginate_by(self, queryset):
        """
        Override get_paginate_by to handle 'view_all' parameter
        If 'view_all' is True, return None to disable pagination
        """
        view_all = self.request.GET.get('view_all') == 'true'
        if view_all:
            return None  # Disable pagination
        return self.paginate_by
    
    def get_queryset(self):
        """
        Mengambil daftar artikel berdasarkan filter dan sorting
        Args:
            self: instance dari kelas ini
        Returns:
            queryset: Daftar artikel yang sudah difilter dan diurutkan
        Notes:
            - Artikel yang ditampilkan adalah artikel dengan status 'published'.
            - Artikel diurutkan berdasarkan tanggal pembuatan terbaru.
            - Filter dan sorting diterapkan berdasarkan parameter GET dari request.
            - Artikel dapat difilter berdasarkan kategori dan pencarian.
            - Artikel dapat diurutkan berdasarkan tanggal terbaru, tanggal terlama, popularitas, atau abjad (A-Z atau Z-A).
        """
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
        """
        get_context_data untuk menambahkan kategori dan artikel unggulan ke konteks
        Args:
            **kwargs: argumen tambahan
        Returns:
            context: konteks yang sudah ditambahkan kategori dan artikel unggulan
        Notes:
            - Kategori yang ditampilkan diambil dari model Category.
            - Artikel unggulan diambil dari model Article dengan atribut is_featured=True.
            - Kategori yang dipilih ditandai dalam UI.
            - Artikel terkait ditampilkan berdasarkan kategori yang sama.
            - Kategori yang dipilih ditampilkan dalam konteks untuk menandai kategori yang sedang aktif.
            - Artikel terkait ditampilkan berdasarkan kategori yang sama.
            - Artikel unggulan ditampilkan di bagian atas daftar artikel.
        """
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
        
        # Add view_all parameter to context
        context['view_all'] = self.request.GET.get('view_all') == 'true'
        
        return context
    
    def render_to_response(self, context, **response_kwargs):
        """
        Override render_to_response to handle AJAX requests
        Args:
            context: Context data for the template
            **response_kwargs: Additional response arguments
        Returns:
            HttpResponse or JsonResponse: Rendered template or JSON data
        """
        is_ajax_request = self.request.headers.get('X-Requested-With') == 'XMLHttpRequest' or self.request.GET.get('ajax') == 'true'
        
        if is_ajax_request:
            # Determine if there's any search or filter applied
            has_search_or_filter = bool(
                self.request.GET.get('search') or 
                self.request.GET.get('category') or 
                self.request.GET.get('sort') or
                self.request.GET.get('view_all') == 'true'
            )
            
            # Render partial templates to strings
            articles_html = render_to_string(
                'partials/article_list.html',
                {'articles': context['articles'], 'page_obj': context.get('page_obj')},
                request=self.request
            )
            
            active_filters_html = render_to_string(
                'partials/active_filters.html',
                {
                    'request': self.request,
                    'selected_category_objects': context['selected_category_objects'],
                    'view_all': context.get('view_all', False)
                },
                request=self.request
            )
            
             # Only render pagination if not in view_all mode
            if self.request.GET.get('view_all') == 'true':
                pagination_html = ''
            else:
                pagination_html = render_to_string(
                    'partials/pagination.html',
                    {
                        'is_paginated': context.get('is_paginated', False),
                        'page_obj': context.get('page_obj'),
                        'paginator': context.get('paginator'),
                        'request': self.request
                    },
                    request=self.request
                )
            
            # Return JSON response
            return JsonResponse({
                'articles_html': articles_html,
                'active_filters_html': active_filters_html,
                'pagination_html': pagination_html,
                'has_search_or_filter': has_search_or_filter,
                'total_articles': context.get('paginator').count if context.get('paginator') else len(context['articles']),
                'current_page': context.get('page_obj').number if context.get('page_obj') else 1,
                'total_pages': context.get('paginator').num_pages if context.get('paginator') else 1,
                'view_all': self.request.GET.get('view_all') == 'true'
            })
        
        # For non-AJAX requests, check if we need to set an initial state for the featured article
        # This ensures the featured article is hidden on initial page load if there's a search query
        context['has_search_or_filter'] = bool(
            self.request.GET.get('search') or 
            self.request.GET.get('category') or 
            self.request.GET.get('sort') or
            self.request.GET.get('view_all') == 'true'
        )
        
        # Regular response for non-AJAX requests
        return super().render_to_response(context, **response_kwargs)


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
    Custom template filter to replace URL parameters
    Args:
        request: HTTP request object
        field (str): Parameter name to replace
        value (str): New value for the parameter
    """
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()
