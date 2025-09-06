from django import forms
from .models import Coupon


class CouponForm(forms.ModelForm):
    """فرم اعمال کوپن"""
    
    class Meta:
        model = Coupon
        fields = ['code']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'کد تخفیف',
                'dir': 'ltr',
                'style': 'text-transform: uppercase;'
            }),
        }
    
    def clean_code(self):
        code = self.cleaned_data.get('code', '').strip().upper()
        if not code:
            raise forms.ValidationError('کد کوپن الزامی است.')
        return code