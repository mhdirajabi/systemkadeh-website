from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView, UpdateView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta
import random
import string
from .models import User, OTPCode, UserAddress, UserProfile
from .forms import (
    UserRegistrationForm, OTPVerificationForm, UserProfileForm,
    UserAddressForm, UserProfileSettingsForm
)
from apps.sms.tasks import send_otp_sms


class LoginView(TemplateView):
    """صفحه ورود با شماره موبایل"""
    template_name = 'accounts/login.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


@require_POST
@csrf_exempt
def send_otp(request):
    """ارسال کد یکبارمصرف"""
    phone = request.POST.get('phone')
    
    if not phone:
        return JsonResponse({'success': False, 'message': 'شماره موبایل الزامی است.'})
    
    # تولید کد ۶ رقمی
    code = ''.join(random.choices(string.digits, k=6))
    
    # ذخیره کد در دیتابیس
    expires_at = timezone.now() + timedelta(minutes=5)
    OTPCode.objects.create(
        phone=phone,
        code=code,
        expires_at=expires_at
    )
    
    # ارسال پیامک
    send_otp_sms.delay(phone, code)
    
    return JsonResponse({
        'success': True,
        'message': f'کد تأیید به شماره {phone} ارسال شد.'
    })


@require_POST
@csrf_exempt
def verify_otp(request):
    """تأیید کد یکبارمصرف و ورود"""
    phone = request.POST.get('phone')
    code = request.POST.get('code')
    
    if not phone or not code:
        return JsonResponse({'success': False, 'message': 'شماره موبایل و کد الزامی است.'})
    
    try:
        otp = OTPCode.objects.get(
            phone=phone,
            code=code,
            is_used=False,
            expires_at__gt=timezone.now()
        )
        
        # علامت‌گذاری کد به عنوان استفاده شده
        otp.is_used = True
        otp.save()
        
        # پیدا کردن یا ایجاد کاربر
        user, created = User.objects.get_or_create(
            phone=phone,
            defaults={
                'username': phone,
                'email': f'{phone}@systemkadeh.com',
                'first_name': 'کاربر',
                'last_name': 'سیستمکده',
                'is_verified': True
            }
        )
        
        if created:
            # ایجاد پروفایل کاربر
            UserProfile.objects.create(user=user)
            messages.success(request, f'حساب کاربری شما با موفقیت ایجاد شد! خوش آمدید {user.first_name}')
        else:
            messages.success(request, f'خوش آمدید {user.full_name}')
        
        # ورود کاربر
        login(request, user)
        
        return JsonResponse({
            'success': True,
            'message': 'ورود موفقیت‌آمیز',
            'redirect_url': request.GET.get('next', '/')
        })
        
    except OTPCode.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'کد نامعتبر یا منقضی شده است.'})


def logout_view(request):
    """خروج از حساب کاربری"""
    logout(request)
    messages.success(request, 'با موفقیت از حساب کاربری خارج شدید.')
    return redirect('core:home')


@login_required
class ProfileView(TemplateView):
    """صفحه پروفایل کاربر"""
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['addresses'] = self.request.user.addresses.all()
        return context


@login_required
class ProfileUpdateView(UpdateView):
    """ویرایش پروفایل"""
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'پروفایل شما با موفقیت به‌روزرسانی شد.')
        return super().form_valid(form)


@login_required
class ProfileSettingsView(UpdateView):
    """تنظیمات پروفایل"""
    model = UserProfile
    form_class = UserProfileSettingsForm
    template_name = 'accounts/profile_settings.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def form_valid(self, form):
        messages.success(self.request, 'تنظیمات شما با موفقیت به‌روزرسانی شد.')
        return super().form_valid(form)


@login_required
class AddressListView(TemplateView):
    """لیست آدرس‌های کاربر"""
    template_name = 'accounts/addresses.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['addresses'] = self.request.user.addresses.all()
        return context


@login_required
class AddressCreateView(TemplateView):
    """افزودن آدرس جدید"""
    template_name = 'accounts/address_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UserAddressForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = UserAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'آدرس جدید با موفقیت اضافه شد.')
            return redirect('accounts:addresses')
        
        context = self.get_context_data()
        context['form'] = form
        return render(request, self.template_name, context)


@login_required
class AddressUpdateView(UpdateView):
    """ویرایش آدرس"""
    model = UserAddress
    form_class = UserAddressForm
    template_name = 'accounts/address_form.html'
    success_url = reverse_lazy('accounts:addresses')
    
    def get_queryset(self):
        return self.request.user.addresses.all()
    
    def form_valid(self, form):
        messages.success(self.request, 'آدرس با موفقیت به‌روزرسانی شد.')
        return super().form_valid(form)


@login_required
@require_POST
def delete_address(request, pk):
    """حذف آدرس"""
    address = get_object_or_404(UserAddress, pk=pk, user=request.user)
    address.delete()
    messages.success(request, 'آدرس با موفقیت حذف شد.')
    return redirect('accounts:addresses')


@login_required
@require_POST
def set_default_address(request, pk):
    """تنظیم آدرس پیش‌فرض"""
    address = get_object_or_404(UserAddress, pk=pk, user=request.user)
    address.is_default = True
    address.save()
    messages.success(request, 'آدرس پیش‌فرض تغییر کرد.')
    return redirect('accounts:addresses')