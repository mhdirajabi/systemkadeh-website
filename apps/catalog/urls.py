from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('search/', views.ProductSearchView.as_view(), name='search'),
    path('featured/', views.FeaturedProductsView.as_view(), name='featured_products'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('brand/<slug:slug>/', views.BrandDetailView.as_view(), name='brand_detail'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
]