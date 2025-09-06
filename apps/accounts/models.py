from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
import uuid


class User(AbstractUser):
    """مدل کاربر سفارشی سیستمکده"""
    
    phone = PhoneNumberField(
        unique=True,
        verbose_name='شماره موبایل'
    )
    email = models.EmailField(
        unique=True,
        verbose_name='ایمیل'
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='نام'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='نام خانوادگی'
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='تاریخ تولد'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='تصویر پروفایل'
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name='تأیید شده'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}' or str(self.phone)
    
    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()


class UserAddress(models.Model):
    """آدرس‌های کاربر"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name='کاربر'
    )
    title = models.CharField(
        max_length=100,
        verbose_name='عنوان آدرس'
    )
    province = models.CharField(
        max_length=50,
        verbose_name='استان'
    )
    city = models.CharField(
        max_length=50,
        verbose_name='شهر'
    )
    address = models.TextField(verbose_name='آدرس کامل')
    postal_code = models.CharField(
        max_length=10,
        verbose_name='کد پستی'
    )
    phone = PhoneNumberField(verbose_name='شماره تلفن')
    is_default = models.BooleanField(
        default=False,
        verbose_name='آدرس پیش‌فرض'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'آدرس کاربر'
        verbose_name_plural = 'آدرس‌های کاربران'
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f'{self.user.full_name} - {self.title}'
    
    def save(self, *args, **kwargs):
        if self.is_default:
            # حذف پیش‌فرض بودن از سایر آدرس‌ها
            UserAddress.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class OTPCode(models.Model):
    """کدهای یکبارمصرف"""
    
    phone = PhoneNumberField(verbose_name='شماره موبایل')
    code = models.CharField(
        max_length=6,
        verbose_name='کد'
    )
    is_used = models.BooleanField(
        default=False,
        verbose_name='استفاده شده'
    )
    expires_at = models.DateTimeField(verbose_name='انقضا')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'کد یکبارمصرف'
        verbose_name_plural = 'کدهای یکبارمصرف'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.phone} - {self.code}'


class UserProfile(models.Model):
    """پروفایل کاربر"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='کاربر'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='درباره من'
    )
    website = models.URLField(
        blank=True,
        verbose_name='وب‌سایت'
    )
    instagram = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='اینستاگرام'
    )
    telegram = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='تلگرام'
    )
    newsletter_subscribed = models.BooleanField(
        default=True,
        verbose_name='عضویت در خبرنامه'
    )
    sms_notifications = models.BooleanField(
        default=True,
        verbose_name='اعلان‌های پیامکی'
    )
    email_notifications = models.BooleanField(
        default=True,
        verbose_name='اعلان‌های ایمیلی'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'پروفایل کاربر'
        verbose_name_plural = 'پروفایل‌های کاربران'
    
    def __str__(self):
        return f'پروفایل {self.user.full_name}'


class UserSession(models.Model):
    """جلسات کاربران"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name='کاربر'
    )
    session_key = models.CharField(
        max_length=40,
        unique=True,
        verbose_name='کلید جلسه'
    )
    ip_address = models.GenericIPAddressField(verbose_name='آدرس IP')
    user_agent = models.TextField(verbose_name='User Agent')
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'جلسه کاربر'
        verbose_name_plural = 'جلسات کاربران'
        ordering = ['-last_activity']
    
    def __str__(self):
        return f'{self.user.full_name} - {self.ip_address}'