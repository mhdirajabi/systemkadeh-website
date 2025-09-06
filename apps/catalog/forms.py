from django import forms
from .models import Product, Category, Brand


class ProductFilterForm(forms.Form):
    """فرم فیلتر محصولات"""
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label="همه دسته‌ها",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.filter(is_active=True),
        required=False,
        empty_label="همه برندها",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'حداقل قیمت'
        })
    )
    
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'حداکثر قیمت'
        })
    )
    
    sort = forms.ChoiceField(
        choices=[
            ('', 'پیش‌فرض'),
            ('price_asc', 'قیمت: کم به زیاد'),
            ('price_desc', 'قیمت: زیاد به کم'),
            ('name_asc', 'نام: الف تا ی'),
            ('name_desc', 'نام: ی تا الف'),
            ('newest', 'جدیدترین'),
            ('popular', 'پرفروش‌ترین'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )