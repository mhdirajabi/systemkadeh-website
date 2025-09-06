from django import forms
from django.contrib.auth.forms import UserCreationForm
from phonenumber_field.formfields import PhoneNumberField
from .models import User, UserAddress, UserProfile


class UserRegistrationForm(UserCreationForm):
    """فرم ثبت‌نام کاربر"""
    
    phone = PhoneNumberField(
        label='شماره موبایل',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '09123456789',
            'dir': 'ltr'
        })
    )
    email = forms.EmailField(
        label='ایمیل',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@email.com',
            'dir': 'ltr'
        })
    )
    first_name = forms.CharField(
        label='نام',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'نام'
        })
    )
    last_name = forms.CharField(
        label='نام خانوادگی',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'نام خانوادگی'
        })
    )
    
    class Meta:
        model = User
        fields = ('phone', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'رمز عبور'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'تکرار رمز عبور'
        })
        for field in self.fields.values():
            if hasattr(field.widget, 'attrs'):
                field.widget.attrs['dir'] = 'rtl' if field.label in ['نام', 'نام خانوادگی'] else 'ltr'


class OTPVerificationForm(forms.Form):
    """فرم تأیید کد یکبارمصرف"""
    
    code = forms.CharField(
        max_length=6,
        min_length=6,
        label='کد تأیید',
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '123456',
            'maxlength': '6',
            'dir': 'ltr',
            'style': 'font-size: 1.5rem; letter-spacing: 0.5rem;'
        })
    )
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code.isdigit():
            raise forms.ValidationError('کد باید شامل اعداد باشد.')
        return code


class UserProfileForm(forms.ModelForm):
    """فرم ویرایش پروفایل"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'birth_date', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام خانوادگی'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ایمیل',
                'dir': 'ltr'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if hasattr(field.widget, 'attrs'):
                field.widget.attrs['dir'] = 'rtl' if field.label in ['نام', 'نام خانوادگی'] else 'ltr'


class UserAddressForm(forms.ModelForm):
    """فرم آدرس کاربر"""
    
    class Meta:
        model = UserAddress
        fields = ['title', 'province', 'city', 'address', 'postal_code', 'phone', 'is_default']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان آدرس (مثل: خانه، محل کار)'
            }),
            'province': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'استان'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'شهر'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'آدرس کامل'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'کد پستی',
                'dir': 'ltr'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '09123456789',
                'dir': 'ltr'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if hasattr(field.widget, 'attrs'):
                field.widget.attrs['dir'] = 'rtl' if field.label not in ['کد پستی', 'شماره تلفن'] else 'ltr'


class UserProfileSettingsForm(forms.ModelForm):
    """فرم تنظیمات پروفایل"""
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'website', 'instagram', 'telegram', 'newsletter_subscribed', 'sms_notifications', 'email_notifications']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'درباره خود بنویسید...'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com',
                'dir': 'ltr'
            }),
            'instagram': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '@username',
                'dir': 'ltr'
            }),
            'telegram': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '@username',
                'dir': 'ltr'
            }),
            'newsletter_subscribed': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'sms_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }