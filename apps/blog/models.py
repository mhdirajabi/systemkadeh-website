from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class BlogCategory(models.Model):
    """دسته‌بندی مقالات وبلاگ"""
    
    name = models.CharField(max_length=100, verbose_name='نام')
    slug = models.SlugField(unique=True, verbose_name='نامک')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'دسته‌بندی وبلاگ'
        verbose_name_plural = 'دسته‌بندی‌های وبلاگ'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog:category_detail', kwargs={'slug': self.slug})


class BlogPost(models.Model):
    """مقالات وبلاگ"""
    
    STATUS_CHOICES = [
        ('draft', 'پیش‌نویس'),
        ('published', 'منتشر شده'),
        ('archived', 'آرشیو شده'),
    ]
    
    title = models.CharField(max_length=300, verbose_name='عنوان')
    slug = models.SlugField(unique=True, verbose_name='نامک')
    content = models.TextField(verbose_name='محتوای مقاله')
    excerpt = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='خلاصه'
    )
    featured_image = models.ImageField(
        upload_to='blog/',
        null=True,
        blank=True,
        verbose_name='تصویر شاخص'
    )
    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='دسته‌بندی'
    )
    author = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='blog_posts',
        verbose_name='نویسنده'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='وضعیت'
    )
    is_featured = models.BooleanField(default=False, verbose_name='ویژه')
    
    # SEO Fields
    meta_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='عنوان سئو'
    )
    meta_description = models.TextField(
        blank=True,
        verbose_name='توضیحات سئو'
    )
    meta_keywords = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='کلمات کلیدی سئو'
    )
    
    # Statistics
    view_count = models.PositiveIntegerField(default=0, verbose_name='تعداد بازدید')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'مقاله وبلاگ'
        verbose_name_plural = 'مقالات وبلاگ'
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class BlogTag(models.Model):
    """برچسب‌های وبلاگ"""
    
    name = models.CharField(max_length=50, unique=True, verbose_name='نام')
    slug = models.SlugField(unique=True, verbose_name='نامک')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'برچسب وبلاگ'
        verbose_name_plural = 'برچسب‌های وبلاگ'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class BlogPostTag(models.Model):
    """ارتباط مقالات و برچسب‌ها"""
    
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, verbose_name='مقاله')
    tag = models.ForeignKey(BlogTag, on_delete=models.CASCADE, verbose_name='برچسب')
    
    class Meta:
        verbose_name = 'برچسب مقاله'
        verbose_name_plural = 'برچسب‌های مقالات'
        unique_together = ['post', 'tag']
    
    def __str__(self):
        return f'{self.post.title} - {self.tag.name}'