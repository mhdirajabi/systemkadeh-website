from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.BlogListView.as_view(), name='post_list'),
    path('category/<slug:slug>/', views.BlogCategoryView.as_view(), name='category_detail'),
    path('<slug:slug>/', views.BlogDetailView.as_view(), name='post_detail'),
    path('latest/', views.latest_posts, name='latest_posts'),
]