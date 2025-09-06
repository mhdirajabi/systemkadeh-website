from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.conf import settings
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'راه‌اندازی اولیه برای محیط تولید'

    def handle(self, *args, **options):
        self.stdout.write('شروع راه‌اندازی محیط تولید...')
        
        # بررسی تنظیمات تولید
        if settings.DEBUG:
            self.stdout.write(
                self.style.WARNING('هشدار: DEBUG=True در محیط تولید!')
            )
        
        # اجرای مایگریشن‌ها
        self.stdout.write('اجرای مایگریشن‌ها...')
        call_command('migrate', verbosity=0)
        
        # جمع‌آوری فایل‌های استاتیک
        self.stdout.write('جمع‌آوری فایل‌های استاتیک...')
        call_command('collectstatic', '--noinput', verbosity=0)
        
        # ایجاد سوپریوزر اگر وجود ندارد
        if not User.objects.filter(is_superuser=True).exists():
            self.stdout.write('ایجاد سوپریوزر...')
            call_command('createsuperuser', interactive=False)
        
        # ایجاد داده نمونه
        self.stdout.write('ایجاد داده نمونه...')
        call_command('create_sample_data')
        
        # بهینه‌سازی پایگاه داده
        self.stdout.write('بهینه‌سازی پایگاه داده...')
        call_command('optimize_db')
        
        self.stdout.write(
            self.style.SUCCESS('راه‌اندازی محیط تولید با موفقیت تکمیل شد!')
        )