from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
from django.core.paginator import Paginator
from .models import Product, Category, Brand, Wishlist
from .forms import ProductFilterForm


class ProductListView(ListView):
    """لیست محصولات"""
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(status='active').select_related('category', 'brand').prefetch_related('images')
        
        # فیلتر دسته‌بندی
        category_slug = self.request.GET.get('category')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)
        
        # فیلتر برند
        brand_slug = self.request.GET.get('brand')
        if brand_slug:
            brand = get_object_or_404(Brand, slug=brand_slug)
            queryset = queryset.filter(brand=brand)
        
        # فیلتر قیمت
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # مرتب‌سازی
        sort = self.request.GET.get('sort')
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'name_asc':
            queryset = queryset.order_by('name')
        elif sort == 'name_desc':
            queryset = queryset.order_by('-name')
        elif sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'popular':
            queryset = queryset.order_by('-sale_count')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['brands'] = Brand.objects.filter(is_active=True)
        return context


class ProductDetailView(DetailView):
    """جزئیات محصول"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        return Product.objects.filter(status='active').select_related('category', 'brand').prefetch_related('images', 'reviews')
    
    def get_object(self):
        obj = super().get_object()
        # افزایش تعداد بازدید
        obj.view_count += 1
        obj.save(update_fields=['view_count'])
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # محصولات مرتبط
        context['related_products'] = Product.objects.filter(
            status='active',
            category=product.category
        ).exclude(id=product.id)[:4]
        
        # بررسی وجود در لیست علاقه‌مندی‌ها
        if self.request.user.is_authenticated:
            context['in_wishlist'] = Wishlist.objects.filter(
                user=self.request.user,
                product=product
            ).exists()
        
        return context


class CategoryDetailView(ListView):
    """محصولات یک دسته‌بندی"""
    model = Product
    template_name = 'catalog/category_detail.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Product.objects.filter(
            status='active',
            category=self.category
        ).select_related('brand').prefetch_related('images')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class BrandDetailView(ListView):
    """محصولات یک برند"""
    model = Product
    template_name = 'catalog/brand_detail.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        self.brand = get_object_or_404(Brand, slug=self.kwargs['slug'])
        return Product.objects.filter(
            status='active',
            brand=self.brand
        ).select_related('category').prefetch_related('images')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brand'] = self.brand
        return context


class ProductSearchView(ListView):
    """جستجوی محصولات"""
    model = Product
    template_name = 'catalog/search_results.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if not query:
            return Product.objects.none()
        
        return Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(short_description__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query),
            status='active'
        ).select_related('category', 'brand').prefetch_related('images')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class FeaturedProductsView(ListView):
    """محصولات ویژه"""
    model = Product
    template_name = 'catalog/featured_products.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        return Product.objects.filter(
            status='active',
            is_featured=True
        ).select_related('category', 'brand').prefetch_related('images')[:8]


@login_required
@require_POST
@csrf_exempt
def add_to_wishlist(request, product_id):
    """افزودن به لیست علاقه‌مندی‌ها"""
    product = get_object_or_404(Product, id=product_id, status='active')
    
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        return JsonResponse({'success': True, 'message': 'به لیست علاقه‌مندی‌ها اضافه شد'})
    else:
        return JsonResponse({'success': False, 'message': 'قبلاً در لیست علاقه‌مندی‌ها موجود است'})


@login_required
@require_POST
@csrf_exempt
def remove_from_wishlist(request, product_id):
    """حذف از لیست علاقه‌مندی‌ها"""
    product = get_object_or_404(Product, id=product_id)
    
    try:
        wishlist_item = Wishlist.objects.get(user=request.user, product=product)
        wishlist_item.delete()
        return JsonResponse({'success': True, 'message': 'از لیست علاقه‌مندی‌ها حذف شد'})
    except Wishlist.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'در لیست علاقه‌مندی‌ها موجود نیست'})