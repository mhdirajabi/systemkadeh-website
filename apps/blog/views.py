from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Q
from .models import BlogPost, BlogCategory, BlogTag
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator


@method_decorator(cache_page(60 * 5), name='dispatch')
class BlogListView(ListView):
    """لیست مقالات وبلاگ"""
    model = BlogPost
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        return BlogPost.objects.filter(
            status='published'
        ).select_related('category', 'author').order_by('-published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = BlogCategory.objects.filter(is_active=True)
        context['featured_posts'] = BlogPost.objects.filter(
            status='published',
            is_featured=True
        )[:3]
        return context


class BlogCategoryView(ListView):
    """مقالات یک دسته‌بندی"""
    model = BlogPost
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        self.category = get_object_or_404(BlogCategory, slug=self.kwargs['slug'])
        return BlogPost.objects.filter(
            status='published',
            category=self.category
        ).select_related('category', 'author').order_by('-published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = BlogCategory.objects.filter(is_active=True)
        return context


class BlogDetailView(DetailView):
    """جزئیات مقاله"""
    model = BlogPost
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        return BlogPost.objects.filter(status='published').select_related('category', 'author')
    
    def get_object(self):
        obj = super().get_object()
        # افزایش تعداد بازدید
        obj.view_count += 1
        obj.save(update_fields=['view_count'])
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # مقالات مرتبط
        context['related_posts'] = BlogPost.objects.filter(
            status='published',
            category=post.category
        ).exclude(id=post.id)[:3]
        
        # مقالات اخیر
        context['recent_posts'] = BlogPost.objects.filter(
            status='published'
        ).exclude(id=post.id)[:5]
        
        return context


@require_GET
@cache_page(60 * 5)
def latest_posts(request):
    """آخرین مقالات برای HTMX"""
    posts = BlogPost.objects.filter(
        status='published'
    ).select_related('category', 'author')[:3]
    
    return render(request, 'blog/latest_posts.html', {'posts': posts})