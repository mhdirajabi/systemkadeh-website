from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.core.models import SiteSettings, Banner
from apps.catalog.models import Category, Brand, Product, ProductImage
from apps.blog.models import BlogCategory, BlogPost
from apps.accounts.models import UserProfile
import random
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'ایجاد داده نمونه برای سیستمکده'

    def handle(self, *args, **options):
        self.stdout.write('شروع ایجاد داده نمونه...')
        
        # ایجاد تنظیمات سایت
        self.create_site_settings()
        
        # ایجاد دسته‌بندی‌ها
        self.create_categories()
        
        # ایجاد برندها
        self.create_brands()
        
        # ایجاد محصولات
        self.create_products()
        
        # ایجاد دسته‌بندی وبلاگ
        self.create_blog_categories()
        
        # ایجاد مقالات وبلاگ
        self.create_blog_posts()
        
        # ایجاد بنرها
        self.create_banners()
        
        self.stdout.write(
            self.style.SUCCESS('داده نمونه با موفقیت ایجاد شد!')
        )

    def create_site_settings(self):
        if not SiteSettings.objects.exists():
            SiteSettings.objects.create(
                site_name='سیستمکده',
                site_description='فروشگاه تخصصی لوازم صوتی، تصویری، مانیتور اندروید و تجهیزات امنیتی خودرو',
                site_keywords='سیستم صوتی خودرو، مانیتور اندروید، تجهیزات امنیتی، سیستمکده',
                phone='021-12345678',
                email='info@systemkadeh.com',
                address='تهران، خیابان ولیعصر، پلاک ۱۲۳',
                instagram='https://instagram.com/systemkadeh',
                telegram='https://t.me/systemkadeh',
                whatsapp='https://wa.me/989123456789',
                currency='تومان',
                currency_symbol='تومان',
                shipping_cost=50000,
                free_shipping_threshold=500000
            )
            self.stdout.write('تنظیمات سایت ایجاد شد')

    def create_categories(self):
        categories_data = [
            {
                'name': 'سیستم صوتی',
                'description': 'بهترین سیستم‌های صوتی خودرو با کیفیت بالا',
                'icon': 'bi-music-note-beamed'
            },
            {
                'name': 'مانیتور اندروید',
                'description': 'مانیتورهای هوشمند اندروید برای خودرو',
                'icon': 'bi-tablet'
            },
            {
                'name': 'دوربین خودرو',
                'description': 'دوربین‌های ثبت تصاویر و فیلم‌برداری',
                'icon': 'bi-camera-video'
            },
            {
                'name': 'آنتن و گیرنده',
                'description': 'آنتن‌ها و گیرنده‌های رادیو و تلویزیون',
                'icon': 'bi-broadcast'
            },
            {
                'name': 'کابل و اتصالات',
                'description': 'کابل‌ها و اتصالات مورد نیاز',
                'icon': 'bi-plug'
            }
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'icon': cat_data['icon'],
                    'is_active': True,
                    'is_featured': True
                }
            )
            if created:
                self.stdout.write(f'دسته‌بندی {category.name} ایجاد شد')

    def create_brands(self):
        brands_data = [
            {'name': 'Pioneer', 'description': 'برند پیشرو در سیستم‌های صوتی'},
            {'name': 'Kenwood', 'description': 'کیفیت و نوآوری در صدا'},
            {'name': 'Sony', 'description': 'تکنولوژی پیشرفته سونی'},
            {'name': 'JVC', 'description': 'تجربه صوتی منحصر به فرد'},
            {'name': 'Alpine', 'description': 'سیستم‌های صوتی حرفه‌ای'},
            {'name': 'Clarion', 'description': 'طراحی و عملکرد عالی'},
        ]
        
        for brand_data in brands_data:
            brand, created = Brand.objects.get_or_create(
                name=brand_data['name'],
                defaults={
                    'description': brand_data['description'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'برند {brand.name} ایجاد شد')

    def create_products(self):
        categories = Category.objects.all()
        brands = Brand.objects.all()
        
        products_data = [
            {
                'name': 'سیستم صوتی Pioneer DEH-X8800BHS',
                'description': 'سیستم صوتی پیشرفته با قابلیت اتصال بلوتوث و USB',
                'price': 2500000,
                'compare_price': 3000000,
                'stock_quantity': 15
            },
            {
                'name': 'مانیتور اندروید 10.1 اینچ',
                'description': 'مانیتور هوشمند اندروید با صفحه نمایش لمسی',
                'price': 4500000,
                'compare_price': 5000000,
                'stock_quantity': 8
            },
            {
                'name': 'دوربین دش‌کم HD 1080P',
                'description': 'دوربین ثبت تصاویر با کیفیت HD و دید در شب',
                'price': 1200000,
                'compare_price': 1500000,
                'stock_quantity': 25
            },
            {
                'name': 'آنتن رادیو AM/FM',
                'description': 'آنتن رادیو با دریافت قوی و کیفیت بالا',
                'price': 350000,
                'compare_price': 400000,
                'stock_quantity': 50
            },
            {
                'name': 'کابل RCA طلایی',
                'description': 'کابل اتصال با کیفیت بالا و کاهش نویز',
                'price': 180000,
                'compare_price': 220000,
                'stock_quantity': 100
            }
        ]
        
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'description': product_data['description'],
                    'short_description': product_data['description'][:100],
                    'price': product_data['price'],
                    'compare_price': product_data['compare_price'],
                    'stock_quantity': product_data['stock_quantity'],
                    'category': random.choice(categories),
                    'brand': random.choice(brands),
                    'status': 'active',
                    'is_featured': True,
                    'sku': f'SK{random.randint(1000, 9999)}'
                }
            )
            if created:
                self.stdout.write(f'محصول {product.name} ایجاد شد')

    def create_blog_categories(self):
        categories_data = [
            {'name': 'راهنمای خرید', 'description': 'راهنمای انتخاب بهترین محصولات'},
            {'name': 'نصب و راه‌اندازی', 'description': 'آموزش نصب و راه‌اندازی تجهیزات'},
            {'name': 'نکات فنی', 'description': 'نکات فنی و تخصصی'},
            {'name': 'اخبار و رویدادها', 'description': 'آخرین اخبار و رویدادهای صنعت'},
        ]
        
        for cat_data in categories_data:
            category, created = BlogCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'دسته‌بندی وبلاگ {category.name} ایجاد شد')

    def create_blog_posts(self):
        categories = BlogCategory.objects.all()
        
        # ایجاد کاربر نویسنده
        author, created = User.objects.get_or_create(
            phone='09123456789',
            defaults={
                'username': 'admin',
                'email': 'admin@systemkadeh.com',
                'first_name': 'مدیر',
                'last_name': 'سیستمکده',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            UserProfile.objects.create(user=author)
        
        posts_data = [
            {
                'title': 'راهنمای انتخاب بهترین سیستم صوتی خودرو',
                'content': 'انتخاب سیستم صوتی مناسب برای خودرو یکی از مهم‌ترین تصمیمات است. در این مقاله به بررسی نکات مهم در انتخاب سیستم صوتی می‌پردازیم...',
                'excerpt': 'راهنمای کامل انتخاب سیستم صوتی خودرو با بررسی نکات مهم و ویژگی‌های کلیدی'
            },
            {
                'title': 'نصب مانیتور اندروید در خودرو',
                'content': 'نصب مانیتور اندروید در خودرو نیاز به دقت و مهارت دارد. در این آموزش گام به گام نصب مانیتور اندروید را بررسی می‌کنیم...',
                'excerpt': 'آموزش کامل نصب مانیتور اندروید در خودرو با تصاویر و توضیحات دقیق'
            },
            {
                'title': 'نکات مهم در انتخاب دوربین خودرو',
                'content': 'دوربین خودرو یکی از تجهیزات امنیتی مهم است. در این مقاله به بررسی نکات مهم در انتخاب دوربین خودرو می‌پردازیم...',
                'excerpt': 'راهنمای انتخاب دوربین خودرو با بررسی ویژگی‌های مهم و نکات فنی'
            }
        ]
        
        for post_data in posts_data:
            post, created = BlogPost.objects.get_or_create(
                title=post_data['title'],
                defaults={
                    'content': post_data['content'],
                    'excerpt': post_data['excerpt'],
                    'category': random.choice(categories),
                    'author': author,
                    'status': 'published',
                    'is_featured': True
                }
            )
            if created:
                self.stdout.write(f'مقاله {post.title} ایجاد شد')

    def create_banners(self):
        banners_data = [
            {
                'title': 'با سیستمکده، صدای ماشینت رو متحول کن!',
                'subtitle': 'بهترین سیستم‌های صوتی با کیفیت و قیمت مناسب',
                'banner_type': 'home'
            },
            {
                'title': 'مانیتورهای اندروید هوشمند',
                'subtitle': 'تجربه رانندگی هوشمند با تکنولوژی پیشرفته',
                'banner_type': 'home'
            }
        ]
        
        for banner_data in banners_data:
            banner, created = Banner.objects.get_or_create(
                title=banner_data['title'],
                defaults={
                    'subtitle': banner_data['subtitle'],
                    'banner_type': banner_data['banner_type'],
                    'is_active': True,
                    'order': len(Banner.objects.all()) + 1
                }
            )
            if created:
                self.stdout.write(f'بنر {banner.title} ایجاد شد')