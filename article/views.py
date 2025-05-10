from django.views.generic import ListView, DetailView
from django.db.models import Q
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
    Notes:
        - Artikel yang ditampilkan adalah artikel dengan status 'published'.
        - Artikel diurutkan berdasarkan tanggal pembuatan terbaru.
        - Halaman artikel menggunakan pagination.
        - Artikel dapat difilter berdasarkan kategori dan pencarian.
        - Artikel dapat diurutkan berdasarkan tanggal terbaru, tanggal terlama, popularitas, atau abjad (A-Z atau Z-A).
        - Kategori yang ditampilkan diambil dari model Category.
        - Artikel unggulan diambil dari model Article dengan atribut is_featured=True.
    """
    model = Article
    template_name = 'article.html'
    context_object_name = 'articles'
    paginate_by = 3  # Show 3 articles per page
    
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
        
        return context


# TODO: bukan kerjaan aldo, bisa lanjutin sendiri sisanya hehe
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