from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'بهینه‌سازی پایگاه داده'

    def handle(self, *args, **options):
        self.stdout.write('شروع بهینه‌سازی پایگاه داده...')
        
        with connection.cursor() as cursor:
            # بهینه‌سازی جداول
            cursor.execute("VACUUM ANALYZE;")
            self.stdout.write('VACUUM ANALYZE اجرا شد')
            
            # بهینه‌سازی ایندکس‌ها
            cursor.execute("REINDEX DATABASE;")
            self.stdout.write('REINDEX DATABASE اجرا شد')
        
        self.stdout.write(
            self.style.SUCCESS('بهینه‌سازی پایگاه داده با موفقیت تکمیل شد!')
        )