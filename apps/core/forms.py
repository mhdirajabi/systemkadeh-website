from django import forms
from .models import ContactMessage, Newsletter


class ContactForm(forms.ModelForm):
    """فرم تماس با ما"""
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام و نام خانوادگی'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ایمیل'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'شماره تلفن'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'موضوع'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'پیام شما'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['dir'] = 'rtl'


class NewsletterForm(forms.ModelForm):
    """فرم عضویت در خبرنامه"""
    
    class Meta:
        model = Newsletter
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ایمیل شما',
                'dir': 'ltr'
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Newsletter.objects.filter(email=email, is_active=True).exists():
            raise forms.ValidationError('این ایمیل قبلاً در خبرنامه عضو شده است.')
        return email