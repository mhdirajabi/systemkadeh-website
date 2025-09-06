from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.catalog.models import Product, Category
from apps.blog.models import BlogPost


class ProductSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8
    
    def items(self):
        return Product.objects.filter(status='active')
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7
    
    def items(self):
        return Category.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class BlogSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6
    
    def items(self):
        return BlogPost.objects.filter(status='published')
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class StaticSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5
    
    def items(self):
        return [
            'core:home',
            'core:about',
            'core:contact',
            'blog:post_list',
        ]
    
    def location(self, item):
        return reverse(item)