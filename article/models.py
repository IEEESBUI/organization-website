from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid
class Category(models.Model):
    """
    model untuk menyimpan kategori artikel
    Args:
        models (Model): Model dari Django
    Attributes:
        name (str): Nama kategori
        slug (str): Slug untuk URL kategori
        description (str): Deskripsi kategori
    Methods:
        __str__(): Mengembalikan nama kategori
        save(): Menyimpan kategori ke database
    Notes:
        - Slug dihasilkan secara otomatis berdasarkan nama kategori saat disimpan.
        - Kategori diurutkan berdasarkan nama.
        - Kategori memiliki deskripsi opsional.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


def article_image_upload_to(instance, filename):
    """
    bikin path gambar dan nama gambar jadi UUID untuk mencegah bentrok antar gambar saat di upload ke server
    Args:
        instance: instance dari model tempat file dilampirkan
        filename (str): nama asli gambar
    Returns:
        str: path ke file gambar yang diupload
    """
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return "article/articles_images/" +filename

class Article(models.Model):
    """
    Model untuk menyimpan artikel
    Args:
        models (Model): Model dari Django
    Attributes:
        title (str): Judul artikel
        slug (str): Slug untuk URL artikel
        author (User): Penulis artikel
        image (ImageField): Gambar artikel
        excerpt (str): Deskripsi pendek artikel
        content (str): Konten artikel
        categories (ManyToManyField): Kategori artikel
        created_at (DateTimeField): Waktu pembuatan artikel
        updated_at (DateTimeField): Waktu pembaruan artikel
        status (str): Status artikel ('draft' atau 'published')
        is_featured (bool): Menandai apakah artikel ditampilkan di halaman utama
        view_count (int): Jumlah tampilan artikel
    Methods:
        __str__(): Mengembalikan judul artikel
        save(): Menyimpan artikel ke database
    Notes:
        - Slug dihasilkan secara otomatis berdasarkan judul artikel saat disimpan ataupun bisa juga ditulis secara manual apabila diinginkan.
        - Gambar artikel diupload ke direktori 'articles_images/' dengan nama file yang unik menggunakan UUID.
        - Artikel diurutkan berdasarkan waktu pembuatan secara menurun.
        - Status artikel dapat berupa 'draft' atau 'published'.
        - Artikel dapat memiliki banyak kategori.
        - Artikel dapat ditandai sebagai 'featured' untuk ditampilkan di halaman utama.
    """
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    image = models.ImageField(upload_to=article_image_upload_to, blank=True, null=True)
    excerpt = models.TextField(help_text="A short description of the article")
    content = models.TextField()  # TODO: ganti jadi rich text editor kalau mau, cuman tergantung kebutuhan juga https://medium.com/@yashnarsamiyev2/how-to-add-ckeditor-in-django-aa6de5a09862
    categories = models.ManyToManyField(Category, related_name='articles')
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """
        update slug saat menyimpan artikel
        """
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)