from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import ContactMessage, Newsletter
from .forms import ContactForm, NewsletterForm


class HomeView(TemplateView):
    """صفحه اصلی سیستمکده"""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # اضافه کردن محصولات ویژه، جدیدترین محصولات و غیره
        return context


class AboutView(TemplateView):
    """درباره ما"""
    template_name = 'core/about.html'


class ContactView(TemplateView):
    """تماس با ما"""
    template_name = 'core/contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContactForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'پیام شما با موفقیت ارسال شد. به زودی با شما تماس خواهیم گرفت.')
            return redirect('core:contact')
        
        context = self.get_context_data()
        context['form'] = form
        return render(request, self.template_name, context)


@require_POST
@csrf_exempt
def newsletter_subscribe(request):
    """عضویت در خبرنامه"""
    form = NewsletterForm(request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True, 'message': 'با موفقیت در خبرنامه عضو شدید!'})
    
    return JsonResponse({'success': False, 'errors': form.errors})


@require_POST
@csrf_exempt
def newsletter_unsubscribe(request):
    """لغو عضویت از خبرنامه"""
    email = request.POST.get('email')
    if email:
        try:
            newsletter = Newsletter.objects.get(email=email)
            newsletter.is_active = False
            newsletter.save()
            return JsonResponse({'success': True, 'message': 'عضویت شما لغو شد.'})
        except Newsletter.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'ایمیل یافت نشد.'})
    
    return JsonResponse({'success': False, 'message': 'ایمیل معتبر نیست.'})